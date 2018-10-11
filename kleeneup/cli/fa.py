from cleo import Command

from kleeneup import FiniteAutomaton, State, Symbol
from kleeneup.util import fa_to_file


def write_file_and_print_table(cmd: Command, fa: FiniteAutomaton):
    out = cmd.option('out')

    transitions = [
        [str(prev_state), str(symbol), str(new_state)]
        for ((prev_state, symbol), new_states) in fa.transitions.items()
        for new_state in new_states
    ]

    transitions.sort()

    cmd.render_table(
        ['previous_state', 'symbol', 'next_state'],
        transitions,
    )

    if out is not None:
        path = fa_to_file(fa, out)
        cmd.info('Wrote finite automaton to {}'.format(path))


class Determinize(Command):
    """
    Determinize a finite automaton

    fa:determinize
        {fa : the automata}
        {--out= : output}
    """

    def handle(self):
        # fa_path = self.argument('fa')
        #
        # fa = fa_from_file(fa_path)

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

        new_fa = fa.determinize()

        write_file_and_print_table(self, new_fa)


class Union(Command):
    """
    Computes the union of two finite automata

    fa:union
        {fa1 : first automata}
        {fa2 : second automata}
    """

    def handle(self):
        fa1 = self.argument('fa1')
        fa2 = self.argument('fa2')

        self.line(fa1)
        self.line(fa2)


class Intersection(Command):
    """
    Computes the intersection of two finite automata

    fa:intersection
        {fa1 : first automata}
        {fa2 : second automata}
    """

    def handle(self):
        fa1 = self.argument('fa1')
        fa2 = self.argument('fa2')

        self.line(fa1)
        self.line(fa2)


commands = [Determinize(), Union(), Intersection()]
