from cleo import Command

from kleeneup import FiniteAutomaton, Sentence, State, Symbol
from kleeneup.util import fa_from_file, fa_to_file


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


class Create(Command):
    """
    Create a stub file for a new automaton

    fa:create
        {out : file to export the automaton}
    """

    def handle(self):
        out = self.argument('out')

        a = Symbol('a')
        b = Symbol('b')

        Q0 = State('Q0')

        fa = FiniteAutomaton(
            {
                (Q0, a): [Q0],
                (Q0, b): [Q0],
            },
            Q0,
            [Q0],
        )

        path = fa_to_file(fa, out)
        self.info('Wrote finite automaton to {}'.format(path))


class Evaluate(Command):
    """
    Evaluate a sentence using a finite automaton

    fa:evaluate
        {fa : the automaton}
        {sentence : the sentence}
    """

    def handle(self):
        fa_path = self.argument('fa')
        sentence = self.argument('sentence')

        fa = fa_from_file(fa_path)

        accepts = fa.evaluate(Sentence(sentence))

        if accepts:
            self.info('Accepted')
        else:
            self.error('Rejected')


class Determinize(Command):
    """
    Determinize a finite automaton

    fa:determinize
        {fa : the automaton}
        {--out= : file to export the resulting automaton}
    """

    def handle(self):
        fa_path = self.argument('fa')

        fa = fa_from_file(fa_path)

        new_fa = fa.determinize()

        write_file_and_print_table(self, new_fa)


class Union(Command):
    """
    Computes the union of two finite automata

    fa:union
        {fa1 : first automaton}
        {fa2 : second automaton}
        {--out= : file to export the resulting automaton}
    """

    def handle(self):
        fa1_path = self.argument('fa1')
        fa2_path = self.argument('fa2')

        fa1 = fa_from_file(fa1_path)
        fa2 = fa_from_file(fa2_path)

        new_fa = fa1.union(fa2)

        write_file_and_print_table(self, new_fa)


class Intersection(Command):
    """
    Computes the intersection of two finite automata

    fa:intersection
        {fa1 : first automaton}
        {fa2 : second automaton}
        {--out= : file to export the resulting automaton}
   """

    def handle(self):
        fa1_path = self.argument('fa1')
        fa2_path = self.argument('fa2')

        fa1 = fa_from_file(fa1_path)
        fa2 = fa_from_file(fa2_path)

        new_fa = fa1.intersection(fa2)

        write_file_and_print_table(self, new_fa)


commands = [Create(), Evaluate(), Determinize(), Union(), Intersection()]
