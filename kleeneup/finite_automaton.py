import networkx as nx

'''
trasitions = {(state, symbol): next_state}
'''


class FiniteAutomaton:
    def __init__(self, transitions, initial_state, final_states):
        self.graph = self.make_graph()

        self.states = set(self.graph.nodes())
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = set(final_states)

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
        ...

    def intersection(self, other):
        ...

    def difference(self, other):
        ...

    def reverse(self):
        ...

    def number_of_states(self):
        return self.graph.number_of_nodes()

    def number_of_transitions(self):
        return self.graph.number_of_edges()

    def make_graph(self):
        graph = nx.MultiDiGraph()
        for k, next_state in transitions.items():
            current_state, symbol = k

            self.graph.add_edge(current_state, next_state, symbol=symbol)

        return graph
