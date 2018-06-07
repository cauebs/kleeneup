from copy import deepcopy
from itertools import combinations, count, product
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Union, NewType, Iterable, Iterator, Mapping
from typing import Tuple, Set, Dict, List, FrozenSet


class Symbol:
    def __init__(self, value: str) -> None:
        if len(value) != 1 or value not in ascii_lowercase + digits + '&':
            raise ValueError('Symbol must be a lowercase letter or a digit')
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<Symbol '{self}'>"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other) -> bool:
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other) -> bool:
        if isinstance(other, Symbol):
            return self.value == other.value
        return NotImplemented


class Sentence:
    def __init__(self, symbols: Union[str, Iterable[Symbol]]) -> None:
        if isinstance(symbols, str):
            symbols = (Symbol(c) for c in symbols)
        self.symbols = list(symbols)

    def __str__(self) -> str:
        return ''.join(s.value for s in self.symbols)

    def __repr__(self) -> str:
        return f"<Sentence '{self}'>"

    def __eq__(self, other) -> bool:
        if isinstance(other, Sentence):
            return self.symbols == other.symbols
        return NotImplemented

    def __iter__(self) -> Iterator[Symbol]:
        return iter(self.symbols)


State = NewType('State', str)


class FiniteAutomaton:
    def __init__(
        self,
        transitions: Mapping[Tuple[State, Symbol], Set[State]],
        initial_state: State,
        accept_states: Iterable[State],
    ) -> None:

        self.states: Set[State] = set()
        self.alphabet: Set[Symbol] = set()
        self._delta: Dict[State, Dict[Symbol, Set[State]]] = {}
        self.initial_state = initial_state
        self.accept_states = set(accept_states)

        for (state, symbol), next_states in transitions.items():
            for next_state in next_states:
                self.add_transition(state, symbol, next_state)

    def add_transition(self, source: State, symbol: Symbol, target: State):
        self.states.add(source)
        self.alphabet.add(symbol)
        self.states.add(target)

        self._delta.setdefault(source, dict()).setdefault(symbol, set())
        self._delta[source][symbol].add(target)

    @property
    def transitions(self) -> Dict[Tuple[State, Symbol], Set[State]]:
        return {
            (state, symbol): next_states
            for state, t in self._delta.items()
            for symbol, next_states in t.items()
        }

    def copy(self) -> 'FiniteAutomaton':
        return deepcopy(self)

    def rename_states(self, table: Mapping[State, State]):
        self.initial_state = table.get(self.initial_state, self.initial_state)
        self.states = {table.get(state, state) for state in self.states}
        self.accept_states = {table.get(state, state)
                              for state in self.accept_states}

        old_transitions = self.transitions
        self._delta = {}

        for (state, symbol), next_states in old_transitions.items():
            for next_state in next_states:
                self.add_transition(
                    table.get(state, state),
                    symbol,
                    table.get(next_state, next_state),
                )

    def prefix_state_names(self, prefix):
        self.rename_states({
            state: f'{prefix}{state}'
            for state in self.states
        })

    def reset_state_names(self):
        trans = {
            state: f'Q{i}'
            for i, state in enumerate(self.states - {self.initial_state}, 1)
        }
        trans[self.initial_state] = 'Q0'
        self.rename_states(trans)

    def to_regular_grammar(self):
        from .regular_grammar import RegularGrammar

        fa = self.copy()

        relevant_states = {
            state
            for state in fa.states
            if fa._delta.get(state) and state != fa.initial_state
        }

        letters = ascii_uppercase.replace('S', '')
        n = len(letters)
        non_terminals = (
            letters[i % n] + "'" * (i // n)
            for i in count()
        )

        table = {fa.initial_state: 'S'}

        for (state, symbol), next_states in fa.transitions.items():
            if state in relevant_states and state not in table:
                table[state] = next(non_terminals)

            for state in next_states:
                if state in relevant_states and state not in table:
                    table[state] = next(non_terminals)

        fa.rename_states(table)

        production_rules = []
        for (state, symbol), next_states in fa.transitions.items():
            for next_state in next_states:
                if fa._delta.get(next_state):
                    production_rules.append((state, symbol, next_state))

                if next_state in fa.accept_states:
                    production_rules.append((state, symbol, ''))

        if fa.initial_state in fa.accept_states:
            production_rules.append(('S', '&', ''))

        def compare_key(rule):
            rule = list(rule)

            for i, r in enumerate(rule):
                if r == 'S':
                    rule[i] = chr(0)

                if r == '&':
                    rule[i] = chr(150)

            return tuple(rule)

        production_rules.sort(key=compare_key)

        return RegularGrammar(production_rules, start_symbol='S')

    def remove_epsilon_transitions(self):
        def epsilon_star(state, epsilon_set=None):
            if epsilon_set is None:
                epsilon_set = set()

            epsilon_set.add(state)
            try:
                next_state = self._delta[state][Symbol('&')]
                for nxt in next_state:
                    epsilon_star(nxt, epsilon_set)
            except KeyError:
                return epsilon_set

            return epsilon_set

        epsilon_star_map = {}
        for state in self.states:
            epsilon_set = epsilon_star(state)
            epsilon_star_map[state] = epsilon_set

        for state, epsilon_set in epsilon_star_map.items():
            for next_state in epsilon_set:
                self._replicate_transitions(next_state, state)
                try:
                    self._delta[state].pop(Symbol('&'))
                except KeyError:
                    pass
                if next_state in self.accept_states:
                    self.accept_states.add(state)

    def determinize(self):
        fa = self.copy()
        fa.remove_epsilon_transitions()

        new_initial_state = frozenset({fa.initial_state})
        pending_states = {new_initial_state}
        new_states = set()

        new_transitions = {}

        while pending_states:
            states = pending_states.pop()

            for symbol in fa.alphabet:
                next_states = frozenset({
                    next_state
                    for state in states
                    for next_state in fa.transitate(state, symbol)
                })

                if not next_states:
                    continue
                new_transitions[(states, symbol)] = {next_states}

                if next_states != states and next_states not in new_states:
                    pending_states.add(next_states)

            new_states.add(states)

        new_fa = FiniteAutomaton(
            new_transitions,
            new_initial_state,
            {
                state
                for state in new_states
                if state.intersection(fa.accept_states)
            }
        )

        new_fa.reset_state_names()
        return new_fa

    def discard_state(self, state: State):
        if self.initial_state == state:
            self.initial_state = None

        self._delta.pop(state, None)
        self.states.discard(state)
        self.accept_states.discard(state)

        for _, next_states in self.transitions.items():
            next_states.discard(state)

    def minimize(self) -> 'FiniteAutomaton':
        fa = self.copy()
        fa.remove_unreachable_states()
        fa.remove_dead_states()

        if fa.initial_state is None:
            q0 = State('Q0')
            return FiniteAutomaton(
                q0,
                {(q0, s): q0 for s in self.alphabet},
                q0,
                set()
            )

        fa.remove_equivalent_states()
        return fa

    def remove_unreachable_states(self):
        reachable = set([self.initial_state])
        checked = set()

        while reachable != checked:
            not_checked = set.difference(self.states, checked)
            for state in set.intersection(not_checked, reachable):
                for symbol, next_states in self._delta.get(state, {}).items():
                    for next_state in next_states:
                        reachable.add(next_state)
                checked.add(state)

        for state in set.difference(self.states, reachable):
            self.discard_state(state)

        self.accept_states = set.intersection(reachable, self.accept_states)
        self.states = reachable
        self.reset_state_names()

    def remove_dead_states(self):
        for state in self.states.copy():
            if self.is_dead(state):
                self.discard_state(state)

    def is_dead(self, state: State) -> bool:
        if state in self.accept_states:
            return False

        return all(
            self.is_dead(s)
            for _, states in self._delta.get(state, {}).items()
            for s in states
        )

    def remove_equivalent_states(self):
        undistinguishable: Set[FrozenSet[State]] = set()

        for pair in combinations(self.states - self.accept_states, 2):
            undistinguishable.add(frozenset(pair))

        for pair in combinations(self.accept_states, 2):
            undistinguishable.add(frozenset(pair))

        while True:
            new_distinguishable_found = False
            undistinguishable_copy = undistinguishable.copy()

            for state_a, state_b in undistinguishable_copy:
                if not self._are_undistinguishable(
                    state_a, state_b, undistinguishable_copy
                ):
                    undistinguishable.remove(frozenset((state_a, state_b)))
                    new_distinguishable_found = True

            if not new_distinguishable_found:
                break

        for state_a, state_b in undistinguishable:
            self._merge_states(state_a, state_b)

    def _are_undistinguishable(
        self,
        state_a: State,
        state_b: State,
        undistinguishable: Set[FrozenSet[State]],
    ) -> bool:
        for symbol in self.alphabet:
            trans_a = frozenset(self.transitate(state_a, symbol))
            trans_b = frozenset(self.transitate(state_b, symbol))
            if trans_a != trans_b:
                if frozenset((trans_a, trans_b)) not in undistinguishable:
                    return False
        return True

    def _merge_states(self, keep: State, discard: State):
        if discard == self.initial_state or keep not in self.states:
            keep, discard = discard, keep

        self._replicate_transitions(discard, keep)
        self.discard_state(discard)

    def transitate(self, state: State, symbol: Symbol) -> Set[State]:
        return self._delta.get(state, {}).get(symbol, set())

    def evaluate(self, sentence: Sentence) -> bool:
        current_states = {self.initial_state}

        for symbol in sentence:
            current_states = {
                next_state
                for state in current_states
                for next_state in self.transitate(state, symbol)
            }

        return any(state in self.accept_states
                   for state in current_states)

    def gen_sentences(self, length: int) -> List[Sentence]:
        current_iteration = {(self.initial_state, '')}

        for i in range(length):
            next_iteration = set()

            for state, sentence in current_iteration:
                for symbol, next_states in self._delta.get(state, {}).items():
                    if symbol != '&':
                        new_sentence = sentence + str(symbol)

                    for next_state in next_states:
                        next_iteration.add((next_state, new_sentence))

            current_iteration = next_iteration

            if not next_iteration:
                break

        return [
            Sentence(sentence)
            for state, sentence in current_iteration
            if state in self.accept_states
        ]

    def complete(self):
        error_state = State('Qerror')

        current_transitions = self.transitions
        for state, symbol in product(self.states.copy(), self.alphabet):
            if (state, symbol) not in current_transitions:
                self.add_transition(state, symbol, error_state)

        if error_state in self.states:
            for symbol in self.alphabet:
                self.add_transition(error_state, symbol, error_state)

    def reverse(self) -> 'FiniteAutomaton':
        fa = self.copy()
        old_transitions = fa.transitions
        fa._delta = {}

        for (state, symbol), next_states in old_transitions.items():
            for next_state in next_states:
                fa.add_transition(next_state, symbol, state)

        new_initial_state = State('_Q0')
        fa.states.add(new_initial_state)

        for state in fa.accept_states:
            fa._replicate_transitions(state, new_initial_state)

        fa.accept_states = {fa.initial_state}
        fa.initial_state = new_initial_state
        fa.reset_state_names()

        return fa

    def kleene_star(self) -> 'FiniteAutomaton':
        fa = self.copy()

        for state in fa.accept_states:
            fa._replicate_transitions(fa.initial_state, state)
        fa.accept_states.add(fa.initial_state)

        return fa

    def __eq__(self, other) -> bool:
        if not isinstance(other, FiniteAutomaton):
            return NotImplemented

        fa = self.intersection(other.negate())
        return fa.is_dead(fa.initial_state)

    def negate(self):
        fa = self.determinize()
        fa.complete()
        fa.accept_states = fa.states - fa.accept_states
        return fa

    def intersection(self, other):
        n_fa1 = self.negate()
        n_fa2 = other.negate()

        n_fa12 = n_fa1.union(n_fa2)

        fa_intersection = n_fa12.negate()
        return fa_intersection

    def difference(self, other):
        fa1 = self.copy()
        n_fa2 = other.negate()

        fa_difference = fa1.intersection(n_fa2)
        return fa_difference

    def _replicate_transitions(self, from_state: State, to_state: State):
        for symbol, next_states in self._delta.get(from_state, {}).items():
            for next_state in next_states:
                self.add_transition(to_state, symbol, next_state)

    def union(self, other: 'FiniteAutomaton') -> 'FiniteAutomaton':
        fa1 = self.copy()
        fa1.prefix_state_names('fa1_')

        fa2 = other.copy()
        fa2.prefix_state_names('fa2_')

        for (state, symbol), next_states in fa2.transitions.items():
            for next_state in next_states:
                fa1.add_transition(state, symbol, next_state)

        initial_state = State('q0')
        fa1.states.add(initial_state)

        fa1.accept_states.update(fa2.accept_states)

        fa1._replicate_transitions(fa1.initial_state, initial_state)
        fa1._replicate_transitions(fa2.initial_state, initial_state)

        fa1.initial_state = initial_state

        fa1.reset_state_names()
        return fa1

    def concatenate(self, other: 'FiniteAutomaton') -> 'FiniteAutomaton':
        fa1 = self.copy()
        fa1.prefix_state_names('fa1_')

        fa2 = other.copy()
        fa2.prefix_state_names('fa2_')

        for (state, symbol), next_states in fa2.transitions.items():
            for next_state in next_states:
                fa1.add_transition(state, symbol, next_state)

        for state in fa1.accept_states:
            fa1._replicate_transitions(fa2.initial_state, state)

        fa1.accept_states = fa2.accept_states

        fa1.reset_state_names()
        return fa1
