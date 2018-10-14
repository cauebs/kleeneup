from pathlib import Path

from kleeneup import FiniteAutomaton, RegularGrammar, Symbol
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

        transitions = {
            (t['previous_state'], Symbol(t['symbol'])): t['next_states']
            for t in fa['transitions']
        }

        return FiniteAutomaton(
            transitions,
            fa['initial_state'],
            fa['accept_states']
        )


def fa_to_file(fa: FiniteAutomaton, filename: str):
    ext = '.fa'

    if not filename.endswith(ext):
        filename = filename + ext

    path = Path(filename)

    with path.open('w') as f:
        fad = {
            'initial_state': fa.initial_state,
            'accept_states': fa.accept_states,
            'transitions': [
                {'previous_state': ps, 'symbol': sym, 'next_states': ns}
                for (ps, sym), ns in fa.transitions.items()
            ],
        }

        dump(fad, f)

    return path


def rg_to_file(rg: RegularGrammar, filename: str):
    ext = '.rg'

    if not filename.endswith(ext):
        filename = filename + ext

    path = Path(filename)

    with path.open('w') as f:
        f.write(str(rg))
        f.write('\n')

    return path


def rg_from_file(filename: str):
    with find_file(filename, 'rg').open() as f:
        content = f.read()
        return RegularGrammar.from_string(content)
