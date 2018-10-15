import re
from itertools import groupby

LHS_REGEX = re.compile(r'^([A-Z]\'*)$', re.X)
RHS_REGEX = re.compile(r'^([a-z0-9])([A-Z]\'*)?|(&)$', re.X)


class MalformedGrammar(Exception):
    pass


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
            try:
                lhs, line = line.split('->')
            except ValueError:
                raise MalformedGrammar
            lhs = lhs.strip()

            lhs_match = LHS_REGEX.fullmatch(lhs).groups()[0]
            if not lhs_match:
                raise MalformedGrammar(repr(lhs))

            if i == 0:
                start_symbol = lhs_match

            for rhs in line.split('|'):
                rhs = rhs.strip()

                rhs_match = RHS_REGEX.fullmatch(rhs)
                if not rhs_match:
                    raise MalformedGrammar(repr(rhs))

                nt, t, e = rhs_match.groups()
                rules.append((lhs_match, nt or e, t))

        return cls(rules, start_symbol)

    def to_finite_automaton(self, rename_states=True):
        from .finite_automaton import FiniteAutomaton, Symbol
        accept_states = {None}
        fa = FiniteAutomaton(dict(), self.start_symbol, accept_states)

        for state, symbol, next_state in self.production_rules:
            if symbol == '&':
                fa.accept_states.add(state)
                continue
            fa.add_transition(state, Symbol(symbol), next_state)

        if rename_states:
            fa.reset_state_names()

        return fa

    def __str__(self):
        return '\n'.join(
            '{} -> '.format(nt1) +
            ' | '.join(
                '{}{}'.format(t, nt2 if nt2 is not None else "")
                for _, t, nt2 in group
            )
            for nt1, group in groupby(self.production_rules, key=lambda x: x[0])
        )

    def __eq__(self, other):
        if not isinstance(other, RegularGrammar):
            return NotImplemented

        return (self.production_rules == other.production_rules and
                self.start_symbol == other.start_symbol)
