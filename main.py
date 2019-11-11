import sys
from PyQt5 import QtWidgets
from utils.CustomWidgets import BaseApp


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    baseapp = BaseApp(mainwindow=MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
