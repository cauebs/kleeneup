from lark import UnexpectedInput, ParseError
from .regular_expression import RegularExpression
from .regular_grammar import RegularGrammar

from .gui import MainWindow


class Control:
    def __init__(self):
        self.main_window = MainWindow(self)
        self.automata = []

        self.main_window.show()

    def automata_list(self):
        return self.automata

    def create_automaton_from_re(self, regex):
        try:
            re = RegularExpression(regex)
            fa = re.to_finite_automaton()
            self.automata.append(fa)
            self.main_window.update_combo_boxes(len(self.automata))
            self.main_window.statusBar().setStyleSheet("color: black")
            self.main_window.statusBar().showMessage(
                f'Autômato M{len(self.automata)} criado pela expressão regular "{regex}"')
        except (UnexpectedInput, ParseError):
            self.main_window.statusBar().setStyleSheet("color: red")
            self.main_window.statusBar().showMessage('Expressão regular inválida')

    def create_automaton_from_rg(self, grammar):
        try:
            rg = RegularGrammar.from_string(grammar)
            fa = rg.to_finite_automaton()
            self.automata.append(fa)
            self.main_window.update_combo_boxes(len(self.automata))
            self.main_window.statusBar().setStyleSheet("color: black")
            self.main_window.statusBar().showMessage(
                f'Autômato M{len(self.automata)} criado pela gramática regular "{", ".join(grammar.splitlines())}"')
        except (ValueError, SyntaxError):
            self.main_window.statusBar().setStyleSheet("color: red")
            self.main_window.statusBar().showMessage('Gramática Regular inválida')
