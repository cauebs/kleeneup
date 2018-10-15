from kleeneup import FiniteAutomaton, Sentence, State, Symbol


def test_copy():
    a, b = Symbol('a'), Symbol('b')
    A, B = State('A'), State('B')

    transitions = {
        (A, a): {B},
        (A, b): {A},
        (B, a): {A},
        (B, b): {B},
    }

    fa1 = FiniteAutomaton(transitions, A, {A})
    fa2 = fa1.copy()

    assert fa1 is not fa2


def test_evaluate():
    a = Symbol('a')

    A, B = State('A'), State('B')
    transitions = {
        (A, a): {B},
        (B, a): {A},
    }

    fa = FiniteAutomaton(transitions, A, {A})

    assert not fa.evaluate(Sentence('aaa'))
    assert fa.evaluate(Sentence(''))
    assert fa.evaluate(Sentence('aa'))


def test_union():
    a, b = Symbol('a'), Symbol('b')

    A, B = State('A'), State('B')
    fa_1 = FiniteAutomaton({(A, a): B}, A, {B})

    C, D = State('C'), State('D')
    fa_2 = FiniteAutomaton({(C, b): D}, C, {D})

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
    fa_1 = FiniteAutomaton({(A, a): B}, A, {B})

    C = State('C')
    D = State('D')
    fa_2 = FiniteAutomaton({(C, a): D}, C, {D})

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
    transitions = {
        (A, a): {A},
        (A, b): {B},
    }

    fa = FiniteAutomaton(transitions, A, {B})

    fa.complete()


def test_negate():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    transitions = {
        (A, a): {A},
        (A, b): {B},
    }

    fa = FiniteAutomaton(transitions, A, {B})

    assert not fa.evaluate(Sentence(''))
    assert not fa.evaluate(Sentence('aaa'))
    assert fa.evaluate(Sentence('ab'))

    n_fa = fa.negate()

    assert n_fa.evaluate(Sentence(''))
    assert n_fa.evaluate(Sentence('aaa'))
    assert not n_fa.evaluate(Sentence('ab'))


def test_remove_unreachable():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    C = State('C')
    D = State('D')
    E = State('E')
    F = State('F')
    G = State('G')
    H = State('H')

    transitions = {
        (A, a): {G},
        (A, b): {B},
        (B, a): {F},
        (B, b): {E},
        (C, a): {C},
        (C, b): {G},
        (D, a): {A},
        (D, b): {H},
        (E, a): {E},
        (E, b): {A},
        (F, a): {B},
        (F, b): {C},
        (G, a): {G},
        (G, b): {F},
        (H, a): {H},
        (H, b): {D},
    }

    fa = FiniteAutomaton(transitions, A, [A, D, G])

    fa.remove_unreachable_states()

    assert len(fa.states) == 6


def test_minimize():
    a = Symbol('a')
    b = Symbol('b')

    A = State('A')
    B = State('B')
    C = State('C')
    D = State('D')
    E = State('E')
    F = State('F')
    G = State('G')
    H = State('H')

    transitions = {
        (A, a): {G},
        (A, b): {B},
        (B, a): {F},
        (B, b): {E},
        (C, a): {C},
        (C, b): {G},
        (D, a): {A},
        (D, b): {H},
        (E, a): {E},
        (E, b): {A},
        (F, a): {B},
        (F, b): {C},
        (G, a): {G},
        (G, b): {F},
        (H, a): {H},
        (H, b): {D},
    }

    fa = FiniteAutomaton(transitions, A, [A, D, G])
    fa = fa.minimize()

    assert len(fa.states) == 3
