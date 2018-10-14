from cleo import Command
from cleo.exceptions import MissingArguments

from kleeneup import RegularExpression
from kleeneup.cli.util import write_file_and_print_table


class ConvertToFA(Command):
    """
    Converts a regular expression to a non-deterministic finite automaton

    re:fa
        {re : the regular expression}
        {out? : file to export the resulting automaton}
    """

    def handle(self):
        regexp = self.argument('re')

        if regexp is None:
            raise MissingArguments('Not enough arguments')

        re = RegularExpression(regexp)

        fa = re.to_finite_automaton()

        write_file_and_print_table(self, fa, self.argument('out'))


commands = [ConvertToFA()]
