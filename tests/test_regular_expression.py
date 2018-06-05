from kleeneup import RegularExpression


def test_to_regular_automaton():
    re = RegularExpression('a.b')
    re.to_finite_automaton()
