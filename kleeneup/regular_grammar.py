import re
from itertools import groupby


LHS_REGEX = re.compile(r'^([A-Z]\'*)$', re.X)
RHS_REGEX = re.compile(r'^([a-z0-9])([A-Z]\'*)?|(&)$', re.X)


class RegularGrammar:
    def __init__(self, production_rules, start_symbol=None):
        self.production_rules = production_rules
        if start_symbol is None:
            start_symbol = self.production_rules[0][0]
        self.start_symbol = start_symbol

    @classmethod
    def from_string(cls, s):
        rules = []

        for i, line in enumerate(s.strip().splitlines()):
            lhs, line = line.split('->')
            lhs = lhs.strip()

            lhs_match = LHS_REGEX.fullmatch(lhs).groups()[0]
            if not lhs_match:
                raise SyntaxError(repr(lhs))

            if i == 0:
                start_symbol = lhs_match

            for rhs in line.split('|'):
                rhs = rhs.strip()

                rhs_match = RHS_REGEX.fullmatch(rhs)
                if not rhs_match:
                    raise SyntaxError(repr(rhs))

                nt, t, e = rhs_match.groups()
                rules.append((lhs_match, nt or e, t))

        return cls(rules, start_symbol)

    def __str__(self):
        return '\n'.join(
            f'{nt1} -> ' + ' | '.join(
                f'{t}{nt2 if nt2 is not None else ""}'
                for _, t, nt2 in group
            )
            for nt1, group in groupby(self.production_rules, key=lambda x: x[0])
        )

    def to_finite_automaton(self):
        from .finite_automaton import FiniteAutomaton
        accept_states = {None}
        fa = FiniteAutomaton(dict(), self.start_symbol, accept_states)

        for state, symbol, next_state in self.production_rules:
            if symbol == '&':
                accept_states.add(state)
                continue
            fa.add_transition(state, symbol, next_state)

        fa.reset_state_names()
        return fa
