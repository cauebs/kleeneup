import sys
import PyQt5.QtWidgets as qtw
from .control import Control


def main():
    app = qtw.QApplication(sys.argv)
    ctrl = Control()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
