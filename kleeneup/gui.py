import PyQt5.QtWidgets as qtw
from PyQt5 import uic


class MainWindow(qtw.QMainWindow):
    def __init__(self, ctrl):
        super(MainWindow, self).__init__()
        self.ctrl = ctrl
        uic.loadUi('./kleeneup/forms/kleeneup.ui', self)

        self.action_open_input.triggered.connect(self.show_input_window)
        self.action_aut2gram.triggered.connect(self.show_export_window)
        self.action_test_automata.triggered.connect(self.show_test_window)

        def update_left_table():
            index = self.fa_select_left.currentIndex()
            self.display_automaton(self.table_left, index)

        def update_center_table():
            index = self.fa_select_center.currentIndex()
            self.display_automaton(self.table_center, index)

        self.fa_select_left.currentIndexChanged.connect(update_left_table)
        self.fa_select_center.currentIndexChanged.connect(update_center_table)
        self.op_select.currentIndexChanged.connect(self.update_center)

        self.apply_op_btn.clicked.connect(self.apply_operation)

    def update_center(self):
        index = self.op_select.currentIndex()
        if index > 3:
            self.fa_select_center.setEnabled(False)
            self.table_center.setEnabled(False)
        else:
            self.fa_select_center.setEnabled(True)
            self.table_center.setEnabled(True)

    def apply_operation(self):
        lhs = self.fa_select_left.currentIndex()
        rhs = self.fa_select_center.currentIndex()

        op = self.op_select.currentIndex()

        if op > 3:
            self.ctrl.apply_operation(lhs, op)
        else:
            self.ctrl.apply_operation(lhs, op, rhs=rhs)

    def display_automaton(self, table, i):
        fa = self.ctrl.automata[i]

        table.setRowCount(len(fa.states))
        table.setColumnCount(len(fa.alphabet))

        for i, state in enumerate(sorted(fa.states)):
            label = ''

            if state in fa.accept_states:
                label += '*'

            if state == fa.initial_state:
                label += '->'

            rows_header = qtw.QTableWidgetItem(label + str(state))
            table.setVerticalHeaderItem(i, rows_header)

            for j, symbol in enumerate(sorted(fa.alphabet)):
                if i == 0:
                    columns_header = qtw.QTableWidgetItem(str(symbol))
                    table.setHorizontalHeaderItem(j, columns_header)

                cell_states = fa.transitate(state, symbol)
                if not cell_states:
                    content = '-'
                elif len(cell_states) == 1:
                    content, *_ = cell_states
                else:
                    content = '{' + ', '.join(sorted(cell_states)) + '}'

                cell = qtw.QTableWidgetItem(content)
                table.setItem(i, j, cell)

    def update_combo_boxes(self, index):
        self.fa_select_left.addItem(f'M{index}')
        self.fa_select_center.addItem(f'M{index}')

    def show_input_window(self):
        self.input_window = InputDialog(self.ctrl)
        self.input_window.show()

    def show_export_window(self):
        self.export_window = GrammarOutDialog(self.ctrl)
        self.export_window.show()

    def show_test_window(self):
        self.test_window = AutomataTestDialog(self.ctrl)
        self.test_window.show()


class AutomataTestDialog(qtw.QDialog):
    def __init__(self, ctrl):
        super(AutomataTestDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/automata_test_dialog.ui', self)
        self.ctrl = ctrl
        self.output = ""

        self.fa_combo.currentIndexChanged.connect(self.change_current_fa)
        self.eval_btn.clicked.connect(self.show_eval_results)
        self.list_btn.clicked.connect(self.show_sentences)

        self.populate_combo_box()

    def show_eval_results(self):
        index = self.fa_combo.currentIndex()

        sentences = self.sentence_input.toPlainText()
        sentences = sentences.replace(' ', '').replace('\n', '').rstrip(';')
        sentences = sentences.split(';')

        results = self.ctrl.eval_sentences(index, sentences)

        text = ""
        text += f"--- Autômato M{index+1} ---\n"
        for s, r in results:
            text += f"'{s}': "
            if r:
                text += "ACEITA\n"
            else:
                text += "REJEITADA\n"
        text += "\n"

        self.output += text
        self.text_output.setPlainText(self.output)

    def show_sentences(self):
        index = self.fa_combo.currentIndex()
        n = self.size_input.value()

        sentences = self.ctrl.list_sentences(index, n)

        text = ""
        text += f"--- Autômato M{index+1} ---\n"
        text += f"Sentenças de tamanho {n}:\n"
        for s in sentences:
            text += f"'{s}'\n"
        text += "\n"

        self.output += text
        self.text_output.setPlainText(self.output)

    def change_current_fa(self):
        index = self.fa_combo.currentIndex()
        self.current_fa = self.ctrl.automata[index]

    def populate_combo_box(self):
        for i in range(0, len(self.ctrl.automata)):
            self.fa_combo.addItem(f'M{i+1}')


class GrammarOutDialog(qtw.QDialog):
    def __init__(self, ctrl):
        super(GrammarOutDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/grammar_out_dialog.ui', self)
        self.ctrl = ctrl

        self.fa_combo.currentIndexChanged.connect(self.display_grammar)

        self.populate_combo_box()

    def populate_combo_box(self):
        for i in range(0, len(self.ctrl.automata)):
            self.fa_combo.addItem(f'M{i+1}')

    def display_grammar(self):
        index = self.fa_combo.currentIndex()
        grammar = self.ctrl.automata[index].to_regular_grammar()
        text = str(grammar)
        self.text_box.setPlainText(text)


class InputDialog(qtw.QDialog):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        super(InputDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/input_dialog.ui', self)

        self.accepted.connect(self.create_automaton)

    def create_automaton(self):
        if self.regex_btn.isChecked():
            self.create_from_re()
        else:
            self.create_from_rg()

    def create_from_re(self):
        re = self.textEdit.toPlainText()
        self.ctrl.create_automaton_from_re(re)

    def create_from_rg(self):
        rg = self.textEdit.toPlainText()
        self.ctrl.create_automaton_from_rg(rg)
