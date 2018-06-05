import PyQt5.QtWidgets as qtw
from PyQt5 import uic


class MainWindow(qtw.QMainWindow):
    def __init__(self, ctrl):
        super(MainWindow, self).__init__()
        self.ctrl = ctrl
        uic.loadUi('./kleeneup/forms/kleeneup.ui', self)

        self.action_open_input.triggered.connect(self.show_input_window)
        self.action_aut2gram.triggered.connect(self.show_export_window)

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
        self.export_window = ExportDialog(self.ctrl)
        self.export_window.show()


class ExportDialog(qtw.QDialog):
    def __init__(self, ctrl):
        super(ExportDialog, self).__init__()
        self.ctrl = ctrl
        uic.loadUi('./kleeneup/forms/export_dialog.ui', self)
        self.populate_combo_box()
        self.accepted.connect(self.show_grammar_out)

    def populate_combo_box(self):
        for i in range(0, len(self.ctrl.automata)):
            self.fa_combo.addItem(f'M{i+1}')

    def show_grammar_out(self):
        index = self.fa_combo.currentIndex()
        grammar = self.ctrl.automata[index].to_regular_grammar()

        text = str(grammar)

        self.grammar_out_window = GrammarOutDialog(
            self.ctrl, text)
        self.grammar_out_window.show()


class GrammarOutDialog(qtw.QDialog):
    def __init__(self, ctrl, txt):
        super(GrammarOutDialog, self).__init__()
        self.ctrl = ctrl
        uic.loadUi('./kleeneup/forms/grammar_out_dialog.ui', self)
        self.text_box.setPlainText(txt)


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
