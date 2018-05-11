import pytest
from kleeneup import FiniteAutomaton

xfail = pytest.xfail


def test_init():
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
    assert fa.alphabet == set(['a', 'b'])


def test_union():
    transitions_1 = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B'
    }

    transitions_2 = {
        ('C', 'b'): 'C',
        ('C', 'a'): 'D'
    }

    fa_1 = FiniteAutomaton(transitions_1, 'A', 'B')
    fa_2 = FiniteAutomaton(transitions_2, 'C', 'D')

    fa_union = FiniteAutomaton.union(fa_1, fa_2)

    transitions_union = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B',
        ('C', 'b'): 'C',
        ('C', 'a'): 'D',
        ('Q0', 'a'): 'A',
        ('Q0', 'a'): 'D',
        ('Q0', 'b'): 'B',
        ('Q0', 'b'): 'C',
    }

    assert fa_union.transitions == transitions_union
    assert fa_union.initial_state == 'Q0'
    assert fa_union.final_states == set(['B', 'D'])


def test_concatenate():
    transitions_1 = {
        ('A', 'a'): 'B'
    }

    transitions_2 = {
        ('C', 'a'): 'D'
    }

    fa_1 = FiniteAutomaton(transitions_1, 'A', 'B')
    fa_2 = FiniteAutomaton(transitions_2, 'C', 'D')

    fa_union = FiniteAutomaton.concatenate(fa_1, fa_2)

    transitions_union = {
        ('A', 'a'): 'B',
        ('C', 'a'): 'D',
        ('B', '&'): 'C'
    }

    assert fa_union.transitions == transitions_union
    assert fa_union.initial_state == 'A'
    assert fa_union.final_states == set('D')


def test_complete():
    transitions = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B'
    }

    fa = FiniteAutomaton(transitions, 'A', 'B')

    complete_fa = fa.complete()

    complete_transitions = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B',
        ('B', 'a'): 'Qerror',
        ('B', 'b'): 'Qerror',
        ('Qerror', 'a'): 'Qerror',
        ('Qerror', 'b'): 'Qerror',
    }

    assert complete_transitions == complete_fa.transitions


def test_negate():
    transitions = {
        ('A', 'a'): 'A',
        ('A', 'b'): 'B'
    }

    fa = FiniteAutomaton(transitions, 'A', 'B')
    fa = fa.complete()

    fa = fa.negate()

    assert fa.final_states == set(['A', 'Qerror'])
