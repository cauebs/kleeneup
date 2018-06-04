from copy import deepcopy
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Union, NewType, Iterable, Iterator, Mapping
from typing import Tuple, Set, Dict


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
            for i, state in enumerate(self.states, 1)
            if state != self.initial_state
        }
        trans[self.initial_state] = 'Q0'
        self.rename_states(trans)

    def to_regular_grammar(self):
        from .regular_grammar import RegularGrammar

        fa = self.copy()

        non_terminals = ascii_uppercase.replace('S', '')
        n = len(non_terminals)

        table = {
            state: non_terminals[i % n] + "'" * (i // n)
            for i, state in enumerate(fa.states - {fa.initial_state})
        }

        table[fa.initial_state] = 'S'
        fa.rename_states(table)

        production_rules = []
        for (state, symbol), next_states in fa.transitions.items():
            for next_state in next_states:
                production_rules.append((state, symbol, next_state))

                if next_state in fa.accept_states:
                    production_rules.append((state, symbol, ''))

        return RegularGrammar(production_rules, start_symbol='S')

#     @classmethod
#     def from_regular_expression(cls, expr):
#         ...

    def determinize(self):
        ...

    def minimize(self):
        fa = self.copy()
        fa.remove_unreachable_states()
        # fa.remove_dead_states()
        if fa.initial_state is None:
            q0 = State('Q0')
            transitions = {}
            for symbol in self.alphabet:
                transitions[(q0, symbol)] = q0

            return FiniteAutomaton(q0, transitions, q0, set())
        else:
            fa_min = fa.remove_equivalent_states()

        return fa_min

    def remove_unreachable_states(self):
        reachable = set([self.initial_state])
        checked = set()

        while reachable != checked:
            not_checked = set.difference(self.states, checked)
            for state in set.intersection(not_checked, reachable):
                for symbol in self.alphabet:
                    reachable.add(list(self._delta[state][symbol])[0])
                checked.add(state)

        for state in set.difference(self.states, reachable):
            self._delta.pop(state)

        self.accept_states = set.intersection(reachable, self.accept_states)
        self.states = reachable
        self.reset_state_names()

    def remove_dead_states(self):
        alive = self.accept_states.copy()
        checked = set()
        while alive != checked:
            for alive_state in set.difference(alive, checked):
                for state in self.states:
                    for symbol in self.alphabet:
                        if list(self._delta[state][symbol])[0] == alive_state:
                            alive.add(state)
                checked.add(alive_state)

        for state in set.difference(self.states, alive):
            self._delta.pop(state)

        if self.initial_state not in alive:
            self.initial_state = None

        self.states = alive

        self.reset_state_names()

    def remove_equivalent_states(self):
        self.complete()

        f = self.accept_states.copy()
        k_f = set.difference(self.states, f)

        class_map = {}
        for state in f:
            class_map[state] = f
        for state in k_f:
            class_map[state] = k_f

        eq_classes = [f, k_f]
        while True:
            old_classes = eq_classes.copy()
            for eq_class in eq_classes:
                new_class = set()
                for i in range(0, len(eq_class)-1):
                    for j in range(i, len(eq_class)):
                        for symbol in self.alphabet:
                            next_i = list(self._delta[list(eq_class)[
                                i]][symbol])[0]
                            next_j = list(self._delta[list(eq_class)[
                                j]][symbol])[0]

                            if class_map[next_i] != class_map[next_j]:
                                new_class.add(list(eq_class)[j])
                                class_map[list(eq_class)[j]] = new_class
                                break

                for eq_class in eq_classes:
                    eq_class = set.difference(eq_class, new_class)

                if len(new_class) > 0:
                    eq_classes.append(new_class)

            if old_classes == eq_classes:
                break

        new_transitions = {}
        i = 0
        class2state_map = {}
        for eq_class in eq_classes:
            new_state = State(f'Q{i}')
            class2state_map[frozenset(eq_class)] = new_state
            i += 1

        for eq_class in eq_classes:
            old_state = list(eq_class)[0]
            for symbol in self.alphabet:
                new_transitions[(class2state_map[frozenset(eq_class)], symbol)
                                ] = {class2state_map[frozenset(class_map[list(self._delta[old_state][symbol])[0]])]}

        new_initial_state = class2state_map[frozenset(
            class_map[self.initial_state])]

        new_accept_states = set()
        for state in self.accept_states:
            new_accept_states.add(class2state_map[frozenset(class_map[state])])

        fa_min = FiniteAutomaton(
            new_transitions,
            new_initial_state,
            new_accept_states
        )

        return fa_min

    def __is_empty_language(self):
        ...

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

    def complete(self):
        error_state = State('Qerror')
        self.states.add(error_state)

        current_transitions = self.transitions
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in current_transitions:
                    self.add_transition(state, symbol, error_state)

    def reverse(self):
        ...

#     def kleene_star(self):
#         ...

    def negate(self):
        fa = self.copy()
        fa.complete()
        fa.accept_states = self.states - self.accept_states
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
        for symbol, next_states in self._delta[from_state].items():
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
