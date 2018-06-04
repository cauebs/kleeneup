from .regular_expression import RegularExpression

from .gui import MainWindow


class Control:
    def __init__(self):
        self.main_window = MainWindow(self)
        self.automata = []

        self.main_window.show()

    def automata_list(self):
        return self.automata

    def create_automaton_from_re(self, regex):
        re = RegularExpression(regex)
        fa = re.to_finite_automaton()
        self.automata.append(fa)
        self.main_window.update_combo_boxes(len(self.automata))
