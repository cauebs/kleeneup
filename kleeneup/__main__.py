import sys
import PyQt5.QtWidgets as qtw
from PyQt5 import uic


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('./kleeneup/forms/kleeneup.ui', self)

        self.action_open_input.triggered.connect(self.show_input_window)
        self.action_aut2gram.triggered.connect(self.show_export_window)

    def show_input_window(self):
        self.input_window = InputDialog()
        self.input_window.show()

    def show_export_window(self):
        self.export_window = ExportDialog()
        self.export_window.show()


class ExportDialog(qtw.QDialog):
    def __init__(self):
        super(ExportDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/export_dialog.ui', self)

        self.accepted.connect(self.show_grammar_out)

    def show_grammar_out(self):
        self.grammar_out_window = GrammarOutDialog()
        self.grammar_out_window.show()


class GrammarOutDialog(qtw.QDialog):
    def __init__(self):
        super(GrammarOutDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/grammar_out_dialog.ui', self)


class InputDialog(qtw.QDialog):
    def __init__(self):
        super(InputDialog, self).__init__()
        uic.loadUi('./kleeneup/forms/input_dialog.ui', self)


def main():
    app = qtw.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
