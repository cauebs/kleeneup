from kleeneup import RegularGrammar


def test_from_and_to_string():
    rules = (
        "S' -> aS | &"
        "S -> aA"
        "A -> aA | bB | a"
        "B -> b"
    )
    rg = RegularGrammar.from_string(rules)

    s = rg.to_string()
    assert RegularGrammar.from_string(s).to_string() == s
