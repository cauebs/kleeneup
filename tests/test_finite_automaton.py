from kleeneup import FiniteAutomaton


def test_finite_automaton_creation():
    transitions = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B',
        ('B', 'b'): 'B',
        ('B', 'a'): 'C',
        ('C', 'a'): 'A'
    }
    fa = FiniteAutomaton(transitions, 'A', 'C')

    assert fa.number_of_states() == 3
    assert fa.number_of_transitions() == 5
    assert fa.states == set(['A', 'B', 'C'])
    assert fa.initial_state == 'A'
    assert fa.final_states == set(['C'])
