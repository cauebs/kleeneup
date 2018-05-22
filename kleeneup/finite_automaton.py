from collections import defaultdict
from string import ascii_lowercase, digits
from typing import DefaultDict, Iterable, Set, Iterator, Union, Dict


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


class State:
    def __init__(self, name: str) -> None:
        self.name = name
        self.transitions: DefaultDict[Symbol, Set['State']] = defaultdict(set)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<State '{self}'>"

    def __getitem__(self, s: Union[Symbol, Sentence]) -> 'StateOverlap':
        if isinstance(s, Symbol):
            return StateOverlap(self.transitions[s])

        states = StateOverlap({self})
        for c in s:
            states = states[c]

        return states

    def __setitem__(self, symbol: Symbol, next_state: 'State') -> None:
        self.transitions[symbol].add(next_state)

    def symbols(self) -> Set[Symbol]:
        return set(self.transitions.keys())


class StateOverlap:
    def __init__(self, states: Iterable[State]) -> None:
        self._states = set(states)

    def __repr__(self) -> str:
        return f"<StateOverlap {self._states}>"

    @property
    def states(self) -> Set[State]:
        return self._states

    def __getitem__(self, s: Union[Symbol, Sentence]) -> 'StateOverlap':
        if isinstance(s, Symbol):
            return StateOverlap(
                state
                for current in self._states
                for state in current[s].states
            )

        states = self
        for c in s:
            states = states[c]

        return states

    def __iter__(self) -> Iterator[State]:
        return iter(self._states)

    def __bool__(self) -> bool:
        return bool(self._states)

    def __contains__(self, state: State) -> bool:
        return state in self._states


class FiniteAutomaton:
    def __init__(
        self,
        states: Iterable[State],
        initial_state: State,
        accept_states: Iterable[State],
    ) -> None:

        self.states = set(states)
        self.alphabet: Set[Symbol] = {
            symbol
            for state in states
            for symbol in state.symbols()
        }

        if initial_state not in states:
            raise ValueError('Argument initial_state must be in states')
        self.initial_state = initial_state

        accept_states = set(accept_states)
        if not accept_states.issubset(states):
            raise ValueError('Argument accept_states must be subset of states')
        self.accept_states = accept_states

    def copy(self) -> 'FiniteAutomaton':
        state_swap: Dict[State, State] = {
            state: State(state.name) for state in self.states
        }

        for state in self.states:
            for symbol, next_state_overlap in state.transitions.items():
                for next_state in next_state_overlap:
                    state_swap[state][symbol] = state_swap[next_state]

        return FiniteAutomaton(
            set(state_swap.values()),
            state_swap[self.initial_state],
            {state_swap[state] for state in self.accept_states},
        )

    def prefix_state_names(self, prefix):
        for state in self.states:
            state.name = f'{prefix}{state.name}'

    def reset_state_names(self):
        self.initial_state.name = 'Q0'
        for i, state in enumerate(self.states):
            if state is self.initial_state:
                continue
            state.name = f'Q{i + 1}'

#     @classmethod
#     def from_regular_grammar(cls, grammar):
#         ...

#     def to_regular_grammar(self):
#         ...

#     @classmethod
#     def from_regular_expression(cls, expr):
#         ...

#     def determinize(self):
#         ...

#     def minimize(self):
#         ...

    def evaluate(self, sentence: Sentence):
        return any(
            state in self.initial_state[sentence]
            for state in self.accept_states
        )

    def complete(self):
        error_state = State('Qerror')

        for state in self.states:
            for symbol in self.alphabet:
                if not state[symbol]:
                    state[symbol] = error_state

        self.states.add(error_state)

    # def reverse(self):
    #     ...

#     def kleene_star(self):
#         ...

    def negate(self):
        self.complete()
        self.accept_states = self.states - self.accept_states

#     def intersection(self, other):
#         ...

#     def difference(self, other):
#         ...

    def union(self, other: 'FiniteAutomaton') -> 'FiniteAutomaton':
        new_initial_state = State('Q0')

        for symbol, states in self.initial_state.transitions.items():
            for state in states:
                new_initial_state[symbol] = state

        for symbol, states in other.initial_state.transitions.items():
            for state in states:
                new_initial_state[symbol] = state

        new_states = set.union(self.states, other.states)
        new_states.add(new_initial_state)

        new_accept_states = set.union(self.accept_states, other.accept_states)

        return FiniteAutomaton(
            new_states,
            new_initial_state,
            new_accept_states,
        ).copy()

    def concatenate(self, other: 'FiniteAutomaton') -> 'FiniteAutomaton':
        new_initial_state = self.initial_state

        for accept_state in self.accept_states:
            for symbol, states in other.initial_state.transitions.items():
                for state in states:
                    accept_state[symbol] = state

        new_states = set.union(self.states, other.states)
        new_states.add(new_initial_state)

        new_accept_states = other.accept_states

        return FiniteAutomaton(
            new_states,
            new_initial_state,
            new_accept_states,
        ).copy()
