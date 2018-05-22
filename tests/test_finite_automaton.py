import pytest
from kleeneup import *

xfail = pytest.xfail


def test_copy():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    A[a] = B
    A[b] = A
    B[a] = A
    B[b] = B

    fa1 = FiniteAutomaton([A, B], A, [A])
    fa2 = fa1.copy()

    assert fa1 is not fa2


def test_evaluate():
    a = Symbol('a')

    A = State('A')
    B = State('B')
    A[a] = B
    B[a] = A

    fa = FiniteAutomaton([A, B], A, [A])

    assert not fa.evaluate(Sentence('aaa'))
    assert fa.evaluate(Sentence(''))
    assert fa.evaluate(Sentence('aa'))


def test_union():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    A[a] = B
    fa_1 = FiniteAutomaton([A, B], A, [B])

    C = State('C')
    D = State('D')
    C[b] = D
    fa_2 = FiniteAutomaton([C, D], C, [D])

    fa_union = FiniteAutomaton.union(fa_1, fa_2)

    assert not fa_1.evaluate(Sentence('b'))
    assert not fa_2.evaluate(Sentence('a'))

    assert fa_union.evaluate(Sentence('a'))
    assert fa_union.evaluate(Sentence('b'))
    assert not fa_union.evaluate(Sentence(''))
    assert not fa_union.evaluate(Sentence('ab'))
    assert not fa_union.evaluate(Sentence('ba'))


def test_concatenate():
    a = Symbol('a')

    A = State('A')
    B = State('B')
    A[a] = B

    C = State('C')
    D = State('D')
    C[a] = D

    fa_1 = FiniteAutomaton([A, B], A, [B])
    fa_2 = FiniteAutomaton([C, D], C, [D])

    fa_concat = FiniteAutomaton.concatenate(fa_1, fa_2)

    assert not fa_concat.evaluate(Sentence(''))
    assert not fa_concat.evaluate(Sentence('a'))
    assert fa_concat.evaluate(Sentence('aa'))
    assert not fa_concat.evaluate(Sentence('aaa'))


def test_complete():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    A[a] = A
    A[b] = B

    fa = FiniteAutomaton([A, B], A, [B])

    complete_fa = fa.complete()

    xfail("Not Implemented")


def test_negate():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    A[a] = A
    A[b] = B

    fa = FiniteAutomaton([A, B], A, [B])

    assert not fa.evaluate(Sentence(''))
    assert not fa.evaluate(Sentence('aaa'))
    assert fa.evaluate(Sentence('ab'))

    fa_n = fa.negate()

    assert fa.evaluate(Sentence(''))
    assert fa.evaluate(Sentence('aaa'))
    assert not fa.evaluate(Sentence('ab'))
