from lark import UnexpectedInput, ParseError
from .regular_expression import RegularExpression
from .regular_grammar import RegularGrammar
from .finite_automaton import FiniteAutomaton, Sentence

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

    def apply_operation(self, lhs, op, rhs=None):
        op_map = {
            0: "union",
            1: "difference",
            2: "intersection",
            3: "concatenation",
            4: "complement",
            5: "reverse",
            6: "kleenestar",
            7: "minimize",
            8: "determinize",
            9: "complete",
        }

        if op_map[op] == "union":
            fa1 = self.automata[lhs]
            fa2 = self.automata[rhs]

            result = FiniteAutomaton.union(fa1, fa2)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "difference":
            fa1 = self.automata[lhs]
            fa2 = self.automata[rhs]

            result = FiniteAutomaton.difference(fa1, fa2)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "intersection":
            fa1 = self.automata[lhs]
            fa2 = self.automata[rhs]

            result = FiniteAutomaton.intersection(fa1, fa2)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "concatenation":
            fa1 = self.automata[lhs]
            fa2 = self.automata[rhs]

            result = FiniteAutomaton.concatenate(fa1, fa2)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "complement":
            fa1 = self.automata[lhs]

            result = FiniteAutomaton.negate(fa1)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "reverse":
            fa1 = self.automata[lhs]

            result = FiniteAutomaton.reverse(fa1)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "kleenestar":
            fa1 = self.automata[lhs]

            result = FiniteAutomaton.kleene_star(fa1)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "minimize":
            fa1 = self.automata[lhs]

            result = FiniteAutomaton.minimize(fa1)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "determinize":
            fa1 = self.automata[lhs]

            result = FiniteAutomaton.determinize(fa1)
            self.automata.append(result)
            self.main_window.update_combo_boxes(len(self.automata))

        elif op_map[op] == "complete":
            fa1 = self.automata[lhs].copy()

            fa1.complete()

            self.automata.append(fa1)
            self.main_window.update_combo_boxes(len(self.automata))

        else:
            raise ValueError

        self.main_window.display_automaton(
            self.main_window.table_right, len(self.automata)-1)

    def list_sentences(self, index, length):
        af = self.automata[index]
        return af.gen_sentences(length)

    def eval_sentences(self, index, sentences):
        af = self.automata[index]
        results = []
        for s in sentences:
            if s == '':
                continue
            if s == '&':
                result = af.evaluate(Sentence(''))
            else:
                result = af.evaluate(Sentence(s))
            results.append((s, result))

        return results
