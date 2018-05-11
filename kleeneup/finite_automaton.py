import networkx as nx

'''
trasitions = {(state, symbol): next_state}
'''


class FiniteAutomaton:
    def __init__(self, transitions, initial_state, final_states):
        self.graph = self.make_graph(transitions)

        self.states = set(self.graph.nodes())
        self.transitions = dict(transitions)
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.alphabet = set()
        for k, v in transitions.items():
            self.alphabet.add(k[1])

    @classmethod
    def from_regular_grammar(cls, rg):
        ...

    def to_regular_grammar(self):
        ...

    @classmethod
    def from_regular_expression(cls, re):
        ...

    def determinize(self):
        ...

    def minimize(self):
        ...

    def evaluate(self, string):
        ...

    # completes undefined transitions
    def complete(self):
        error_state = 'Qerror'

        transitions = self.transitions
        states = self.states
        states.add(error_state)

        for state in states:
            for symbol in self.alphabet:
                try:
                    self.transitions[state, symbol]
                except KeyError:
                    transitions[state, symbol] = error_state

        return FiniteAutomaton(
            transitions,
            self.initial_state,
            self.final_states
        )

    def reverse(self):
        ...

    def kleene_star(self):
        ...

    def negate(self):
        ...

    def intersection(self, other):
        ...

    def difference(self, other):
        ...

    def union(self, other):
        # Makes a new state
        initial_state = 'Q0'

        # Union of transition functions
        transitions = self.transitions
        transitions.update(other.transitions)

        # Copy old initial states transitions to new initial state
        for symbol in self.alphabet:
            transitions[
                (initial_state, symbol)
            ] = self.transitions[(self.initial_state, symbol)]
            transitions[
                (initial_state, symbol)
            ] = other.transitions[(other.initial_state, symbol)]

        # Union of final states
        final_states = set.union(self.final_states, other.final_states)

        return FiniteAutomaton(transitions, initial_state, final_states)

    def concatenate(self, other):
        # Union of transition functions
        transitions = self.transitions
        transitions.update(other.transitions)

        for state in self.final_states:
            transitions[(state, '&')] = other.initial_state

        return FiniteAutomaton(
            transitions,
            self.initial_state,
            other.final_states
        )

    def number_of_states(self):
        return self.graph.number_of_nodes()

    def number_of_transitions(self):
        return self.graph.number_of_edges()

    def make_graph(self, transitions):
        graph = nx.MultiDiGraph()
        for k, next_state in transitions.items():
            current_state, symbol = k

            graph.add_edge(current_state, next_state, symbol=symbol)

        return graph
