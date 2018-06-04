import PyQt5.QtWidgets as qtw
from PyQt5 import uic


class MainWindow(qtw.QMainWindow):
    def __init__(self, ctrl):
        super(MainWindow, self).__init__()
        self.ctrl = ctrl
        uic.loadUi('./kleeneup/forms/kleeneup.ui', self)

        self.action_open_input.triggered.connect(self.show_input_window)
        self.action_aut2gram.triggered.connect(self.show_export_window)

        self.fa_select_left.currentIndexChanged.connect(
            lambda: self.display_automaton(self.table_left, self.fa_select_left.currentIndex()))

        self.fa_select_center.currentIndexChanged.connect(
            lambda: self.display_automaton(self.table_center, self.fa_select_center.currentIndex()))

    def display_automaton(self, table, i):
        fa = self.ctrl.automata[i]

        table.setRowCount(len(fa.states))
        table.setColumnCount(len(fa.alphabet))

        for i, state in enumerate(sorted(fa.states)):
            label = str(state)

            if state in fa.accept_states:
                label = f'*{label}'
            if state == fa.initial_state:
                label = f'->{label}'

            table.setVerticalHeaderItem(
                i, qtw.QTableWidgetItem(label))
            for j, symbol in enumerate(sorted(fa.alphabet)):
                if i == 0:
                    table.setHorizontalHeaderItem(
                        j, qtw.QTableWidgetItem(str(symbol)))
                table.setItem(
                    i, j, qtw.QTableWidgetItem(str(fa.transitate(state, symbol) or '-')))

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
        self.ctrl = ctrl
        super(ExportDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/export_dialog.ui', self)

        self.accepted.connect(self.show_grammar_out)

    def show_grammar_out(self):
        self.grammar_out_window = GrammarOutDialog(self.ctrl)
        self.grammar_out_window.show()


class GrammarOutDialog(qtw.QDialog):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        super(GrammarOutDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/grammar_out_dialog.ui', self)


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
