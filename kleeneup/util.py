from pathlib import Path

from kleeneup import FiniteAutomaton
from kleeneup.jayzon import dump, load


class FileNotFound(Exception):
    pass


def find_file(filename: str, ext: str) -> Path:
    if not filename.endswith('.' + ext):
        filename = filename + '.' + ext

    path = Path(filename)

    if path.exists():
        return path

    raise FileNotFound('{} does not exist'.format(filename))


def fa_from_file(filename: str) -> FiniteAutomaton:
    with find_file(filename, 'fa').open() as f:
        fa = load(f)

        return FiniteAutomaton(
            fa['transitions'],
            fa['initial_state'],
            fa['accept_states']
        )


def fa_to_file(fa: FiniteAutomaton, filename: str):
    ext = 'fa'

    if not filename.endswith('.' + ext):
        filename = filename + '.' + ext

    path = Path(filename)

    with path.open('w') as f:
        fad = {
            'transitions': [[ps, sym, ns] for (ps, sym), ns in fa.transitions.items()],
            'initial_state': fa.initial_state,
            'accept_states': fa.accept_states,
        }

        dump(fad, f)

    return path
