import re


LHS_REGEX = re.compile(r'([A-Z]\'*)')
RHS_REGEX = re.compile(r'([a-z0-9&])([A-Z]\'*)?')


def parse_rules(line):
    lhs, rhs = line.split('->', maxsplit=1)

    head = LHS_REGEX.findall(lhs)[0]
    return [(head, *RHS_REGEX.findall(body)[0])
            for body in rhs.split('|')]


class RegularGrammar:
    def __init__(self, production_rules, start_symbol=None):
        self.production_rules = production_rules
        if start_symbol is None:
            start_symbol = self.production_rules[0][0]
        self.start_symbol = start_symbol

    @classmethod
    def from_string(cls, s):
        return cls([rule
                    for line in s.strip().splitlines()
                    for rule in parse_rules(line)])

    def to_string(self):
        return '\n'.join(
            '{} -> {}{}'.format(*rule)
            for rule in self.production_rules
        )

    def to_finite_automaton(self):
        from .finite_automaton import FiniteAutomaton

        transitions = {}
        for state, symbol, next_state in self.production_rules:
            transitions.setdefault((state, symbol), set()).add(next_state)

        fa = FiniteAutomaton(transitions, self.start_symbol, {''})
        fa.reset_state_names()
        return fa
