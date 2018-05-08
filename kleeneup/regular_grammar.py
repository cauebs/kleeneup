import re


LHS_REGEX = re.compile(r'([A-Z]\'*)')
RHS_REGEX = re.compile(r'([a-z0-9&])([A-Z]\'*)?')


def parse_rules(line):
    lhs, rhs = line.split('->', maxsplit=1)

    head = LHS_REGEX.findall(lhs)[0]
    return [(head, *RHS_REGEX.findall(body)[0])
            for body in rhs.split('|')]


class RegularGrammar:
    def __init__(self, production_rules):
        self._production_rules = production_rules

    @classmethod
    def from_string(cls, s):
        return cls([rule
                    for line in s.strip().splitlines()
                    for rule in parse_rules(line)])

    def to_string(self):
        return '\n'.join(
            '{} -> {}{}'.format(*rule)
            for rule in self._production_rules
        )

    def to_finite_automaton(self):
        ...
