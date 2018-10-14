from typing import Optional

from cleo import Command

from kleeneup import FiniteAutomaton
from kleeneup.util import fa_to_file


def str_set_of_states(states):
    return ', '.join(sorted(states))


def str_prev_state(prev_state, fa):
    prefix = ''

    if prev_state == fa.initial_state:
        prefix += '->'

    if prev_state in fa.accept_states:
        prefix += '*'

    return prefix.rjust(3, ' ') + prev_state


def write_file_and_print_table(cmd: Command, fa: FiniteAutomaton, out: Optional[str]):
    alphabet = sorted(fa.alphabet)

    transitions = []

    for state in sorted(fa.states):
        line = [str_prev_state(state, fa)]

        for symbol in alphabet:
            new_state = fa.transitate(state, symbol)

            line.append(str_set_of_states(new_state))

        transitions.append(line)

    cmd.render_table(
        ['K \ Σ', *[str(s) for s in alphabet]],
        transitions,
    )

    if out is not None:
        path = fa_to_file(fa, out)
        cmd.info('Wrote finite automaton to {}'.format(path))
