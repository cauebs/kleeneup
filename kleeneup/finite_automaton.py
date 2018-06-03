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

#     def determinize(self):
#         ...

#     def minimize(self):
#         ...

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
        self.complete()
        self.accept_states = self.states - self.accept_states

#     def intersection(self, other):
#         ...

#     def difference(self, other):
#         ...

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
