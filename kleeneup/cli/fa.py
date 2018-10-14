from cleo import Command
from cleo.exceptions import MissingArguments

from kleeneup import FiniteAutomaton, Sentence, State, Symbol
from kleeneup.cli.util import write_file_and_print_table
from kleeneup.util import fa_from_file, rg_to_file


class Create(Command):
    """
    Creates a stub file for a new automaton

    fa:create
        {out : file to export the automaton}
    """

    def handle(self):
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

        write_file_and_print_table(self, fa, self.argument('out'))


class Evaluate(Command):
    """
    Evaluates a sentence using a finite automaton

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
    Determinizes a finite automaton

    fa:determinize
        {fa : the automaton}
        {out? : file to export the resulting automaton}
    """

    def handle(self):
        fa_path = self.argument('fa')

        fa = fa_from_file(fa_path)

        new_fa = fa.determinize()

        write_file_and_print_table(self, new_fa, self.argument('out'))


class Minimize(Command):
    """
    Minimizes a finite automaton

    fa:minimize
        {fa : the automaton}
        {out? : file to export the resulting automaton}
    """

    def handle(self):
        fa_path = self.argument('fa')

        fa = fa_from_file(fa_path)

        new_fa = fa.minimize()

        write_file_and_print_table(self, new_fa, self.argument('out'))


class Union(Command):
    """
    Computes the union of two finite automata

    fa:union
        {fa1 : first automaton}
        {fa2 : second automaton}
        {out? : file to export the resulting automaton}
    """

    def handle(self):
        fa1_path = self.argument('fa1')
        fa2_path = self.argument('fa2')

        fa1 = fa_from_file(fa1_path)
        fa2 = fa_from_file(fa2_path)

        new_fa = fa1.union(fa2)

        write_file_and_print_table(self, new_fa, self.argument('out'))


class Intersection(Command):
    """
    Computes the intersection of two finite automata

    fa:intersection
        {fa1 : first automaton}
        {fa2 : second automaton}
        {out? : file to export the resulting automaton}
   """

    def handle(self):
        fa1_path = self.argument('fa1')
        fa2_path = self.argument('fa2')

        fa1 = fa_from_file(fa1_path)
        fa2 = fa_from_file(fa2_path)

        new_fa = fa1.intersection(fa2)

        write_file_and_print_table(self, new_fa, self.argument('out'))


class ConvertToRG(Command):
    """
    Converts an automaton to a regular grammar

    fa:rg
        {fa : the automaton}
        {out? : file to export the resulting grammar}
    """

    def handle(self):
        fa_path = self.argument('fa')
        out = self.argument('out')

        if fa_path is None:
            raise MissingArguments('Not enough arguments')

        fa = fa_from_file(fa_path)

        rg = fa.to_regular_grammar()

        self.line(str(rg))

        if out is not None:
            path = rg_to_file(rg, out)
            self.info('Wrote regular grammar to {}'.format(path))


commands = [Create(), Evaluate(), Determinize(), Minimize(), Union(), Intersection(), ConvertToRG()]
