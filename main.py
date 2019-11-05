import sys, os, json
from utils import Core, Forms
from PyQt5 import QtCore, QtWidgets
from functools import partial


class BaseApp:
    def __init__(self, mainwindow):
        print("BaseApp: Instantiating")
        self.pin_list = []
        mainwindow.resize(800, 600)
        mainwindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        mainwindow.setCentralWidget(self.centralwidget)
        self.centralwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.gridLayoutWidget = QtWidgets.QGridLayout(self.centralwidget)
        self.core = Core.Core(layout=self.gridLayoutWidget, comm_args=None)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))

        self.menuArchivo = QtWidgets.QMenu(self.menubar)
        self.menuConexion = QtWidgets.QMenu(self.menuArchivo)
        self.connForm = None
        self.menuBoards = QtWidgets.QMenu(self.menuArchivo)

        self.menuHerramientas = QtWidgets.QMenu(self.menubar)
        self.menuLoggers = QtWidgets.QMenu(self.menuHerramientas)

        mainwindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        mainwindow.setStatusBar(self.statusbar)

        # Instanciamos los QAction
        self.actionNuevo = QtWidgets.QAction(MainWindow)
        self.actionCargar = QtWidgets.QAction(MainWindow)
        self.actionSerial = QtWidgets.QAction(MainWindow)
        self.actionBluetooth = QtWidgets.QAction(MainWindow)
        self.actionIP = QtWidgets.QAction(MainWindow)
        self.actionComm = QtWidgets.QAction(MainWindow)
        self.actionI2C = QtWidgets.QAction(MainWindow)
        self.actionSPI = QtWidgets.QAction(MainWindow)
        self.actionTabla = QtWidgets.QAction(MainWindow)
        self.actionGrafica = QtWidgets.QAction(MainWindow)

        # Añadimos los triggers
        args1 = {'type': 'Serial', 'core': self.core}
        self.actionSerial.triggered.connect(partial(self.set_connform, args=args1))
        args2 = {'type': 'WiFi', 'core': self.core}
        self.actionIP.triggered.connect(partial(self.set_connform, args=args2))
        schemas = os.listdir("resources\\schemas")
        self.actionGrafica.triggered.connect(self.ini_graph_dialog)

        for schema in schemas:
            fd = open("resources\\schemas\\"+schema, 'r')
            data = json.load(fd)
            qaction = QtWidgets.QAction(MainWindow)
            qaction.setText(data['meta']['ui'])
            print(data['pin'])
            qaction.triggered.connect(partial(self.set_pin_list, arg_data=data['pin']))
            self.menuBoards.addAction(qaction)
            fd.close()

        self.menuConexion.addAction(self.actionSerial)
        self.menuConexion.addAction(self.actionBluetooth)
        self.menuConexion.addAction(self.actionIP)

        self.menuArchivo.addAction(self.actionNuevo)
        self.menuArchivo.addAction(self.actionCargar)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.menuConexion.menuAction())
        self.menuArchivo.addAction(self.menuBoards.menuAction())
        self.menuLoggers.addAction(self.actionComm)
        self.menuLoggers.addAction(self.actionI2C)
        self.menuLoggers.addAction(self.actionSPI)
        self.menuHerramientas.addAction(self.menuLoggers.menuAction())
        self.menuHerramientas.addAction(self.actionGrafica)
        self.menuHerramientas.addAction(self.actionTabla)
        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuHerramientas.menuAction())

        self.retranslate_ui(mainwindow)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

        # Hacemos que actuen a los triggers para loggers
        self.actionI2C.triggered.connect(partial(self.core.create_logger_widget, log_id='I2C'))
        self.actionSPI.triggered.connect(partial(self.core.create_logger_widget, log_id='SPI'))
        self.actionComm.triggered.connect(partial(self.core.create_logger_widget, log_id='SERIAL'))

        print("BaseApp: Instanciado")

    def retranslate_ui(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuArchivo.setTitle(_translate("MainWindow", "Archivo"))
        self.menuConexion.setTitle(_translate("MainWindow", "Conexion"))
        self.menuBoards.setTitle(_translate("MainWindow", "Boards"))
        self.actionIP.setText(_translate("MainWindow", "IP"))
        self.menuHerramientas.setTitle(_translate("MainWindow", "Herramientas"))
        self.menuLoggers.setTitle(_translate("MainWindow", "Loggers"))
        self.actionGrafica.setText(_translate("MainWindow", "Graficas"))
        self.actionNuevo.setText(_translate("MainWindow", "Nuevo"))
        self.actionCargar.setText(_translate("MainWindow", "Cargar"))
        self.actionSerial.setText(_translate("MainWindow", "Serial"))
        self.actionBluetooth.setText(_translate("MainWindow", "Bluetooth"))
        self.actionComm.setText(_translate("MainWindow", "Comm"))
        self.actionI2C.setText(_translate("MainWindow", "I2C"))
        self.actionSPI.setText(_translate("MainWindow", "SPI"))
        self.actionTabla.setText(_translate("MainWindow", "Tabla"))

    def ini_graph_dialog(self):
        if self.pin_list:
            print("BaseApp: Creating PlotForm")
            Forms.PlotForm(self.core, self.pin_list)
        else:
            error_msg = QtWidgets.QErrorMessage()
            error_msg.showMessage("Please select a board first")
            error_msg.exec_()

    def set_pin_list(self, arg_data):
        self.pin_list = arg_data

    def set_connform(self, args):
        print('BaseApp: Creating ConnectionForm')
        self.connForm = Forms.ConnectionForm(args)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    baseapp = BaseApp(mainwindow=MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
