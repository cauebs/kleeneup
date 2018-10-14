from cleo import Command
from cleo.exceptions import MissingArguments

from kleeneup import RegularGrammar
from kleeneup.cli.util import write_file_and_print_table
from kleeneup.util import rg_from_file, rg_to_file


class Create(Command):
    """
    Creates a stub file for a new grammar

    rg:create
        {out : file to export the grammar}
    """

    def handle(self):
        out = self.argument('out')

        rg = RegularGrammar.from_string('''
            S' -> aS | bS | &
            S -> aS | bS | a | b
        ''')

        path = rg_to_file(rg, out)
        self.line(str(rg))
        self.info('Wrote regular grammar to {}'.format(path))


class ConvertToFA(Command):
    """
    Converts a grammar to a non-deterministic finite automaton

    rg:fa
        {rg : the grammar}
        {out? : file to export the resulting automaton}
    """

    def handle(self):
        rg_path = self.argument('rg')

        if rg_path is None:
            raise MissingArguments('Not enough arguments')

        rg = rg_from_file(rg_path)

        fa = rg.to_finite_automaton()

        write_file_and_print_table(self, fa, self.argument('out'))


commands = [Create(), ConvertToFA()]
