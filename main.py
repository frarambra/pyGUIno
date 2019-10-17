import sys
import os
import json
from utils import Core
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial


class BaseApp:
    def __init__(self, mainwindow):
        mainwindow.resize(800, 600)
        mainwindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        mainwindow.setCentralWidget(self.centralwidget)
        self.centralwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.gridLayoutWidget = QtWidgets.QGridLayout(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))

        self.menuArchivo = QtWidgets.QMenu(self.menubar)
        self.menuConexion = QtWidgets.QMenu(self.menuArchivo)
        self.connForm = None
        self.menuBoards = QtWidgets.QMenu(self.menuArchivo)

        self.menuHerramientas = QtWidgets.QMenu(self.menubar)
        self.menuLoggers = QtWidgets.QMenu(self.menuHerramientas)
        self.menuGraficas = QtWidgets.QMenu(self.menuHerramientas)

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

        # Añadimos los triggers
        self.actionSerial.triggered.connect(partial(self.set_connform, selected="Serial"))
        self.actionIP.triggered.connect(partial(self.set_connform, selected="WiFi"))
        schemas = os.listdir("resources\\schemas")

        for schema in schemas:
            fd = open("resources\\schemas\\"+schema, 'r')
            data = json.load(fd)
            qaction = QtWidgets.QAction(MainWindow)
            qaction.setText(data['meta']['ui'])
            qaction.triggered.connect(partial(self.update_graphmenu, arg_data=data))
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
        self.menuHerramientas.addAction(self.menuGraficas.menuAction())
        self.menuHerramientas.addAction(self.actionTabla)
        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuHerramientas.menuAction())

        self.retranslate_ui(mainwindow)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

        # Una vez creado todas las toolbars, procedemos a crear el core
        self.core = Core.Core(layout=self.gridLayoutWidget, comm_args=None, list_widgets=None)

        # Hacemos que actuen a los triggers para loggers
        self.actionI2C.triggered.connect(partial(self.core.create_logger_widget, log_id='I2C'))
        self.actionSPI.triggered.connect(partial(self.core.create_logger_widget, log_id='SPI'))
        self.actionComm.triggered.connect(partial(self.core.create_logger_widget, log_id='COM'))

    def retranslate_ui(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuArchivo.setTitle(_translate("MainWindow", "Archivo"))
        self.menuConexion.setTitle(_translate("MainWindow", "Conexion"))
        self.menuBoards.setTitle(_translate("MainWindow", "Boards"))
        self.actionIP.setText(_translate("MainWindow", "IP"))
        self.menuHerramientas.setTitle(_translate("MainWindow", "Herramientas"))
        self.menuLoggers.setTitle(_translate("MainWindow", "Loggers"))
        self.menuGraficas.setTitle(_translate("MainWindow", "Graficas"))
        self.actionNuevo.setText(_translate("MainWindow", "Nuevo"))
        self.actionCargar.setText(_translate("MainWindow", "Cargar"))
        self.actionSerial.setText(_translate("MainWindow", "Serial"))
        self.actionBluetooth.setText(_translate("MainWindow", "Bluetooth"))
        self.actionComm.setText(_translate("MainWindow", "Comm"))
        self.actionI2C.setText(_translate("MainWindow", "I2C"))
        self.actionSPI.setText(_translate("MainWindow", "SPI"))
        self.actionTabla.setText(_translate("MainWindow", "Tabla"))

    def update_graphmenu(self, arg_data):
        # El input son los datos de la placa guardados en .json
        # Hay que actualizar los menus:
        for pin in arg_data['analogico']:
            # TODO: Vaciar y entonces añadir pines
            qaction = QtWidgets.QAction(MainWindow)
            qaction.setText('Pin '+pin)
            self.menuGraficas.addAction(qaction)
            qaction.triggered.connect(partial(self.core.create_plot_widget, pin=pin))

    def set_connform(self, selected):
        self.connForm = ConnectionForm(selected)


class ConnectionForm(QtWidgets.QDialog):
    # Sera el formulario para realizar la conexion, sea cual sea
    def __init__(self, selected):
        # TODO: Comprobar datos de entrada y añadir las funciones a los botones
        QtWidgets.QDialog.__init__(self)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.dialogLayout = QtWidgets.QVBoxLayout()
        self.formBox = QtWidgets.QGroupBox(selected)
        formlayout = QtWidgets.QFormLayout()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Conexion")

        if selected == 'Serial':
            self.qlabel1 = QtWidgets.QLabel(self.formBox)
            self.qlabel2 = QtWidgets.QLabel(self.formBox)
            self.qlabel1.setText('Serial')
            self.qlabel2.setText('Baudrate')
            self.i1 = QtWidgets.QLineEdit()
            self.i2 = QtWidgets.QLineEdit()
            formlayout.addRow(self.qlabel1, self.i1)
            formlayout.addRow(self.qlabel2, self.i2)

        elif selected == 'WiFi':
            self.qlabel1 = QtWidgets.QLabel(self.formBox)
            self.qlabel2 = QtWidgets.QLabel(self.formBox)
            self.qlabel1.setText('IP')
            self.qlabel2.setText('Puerto')
            self.transport = QtWidgets.QComboBox()
            self.transport.addItem("TCP")
            self.transport.addItem("UDP")
            self.i1 = QtWidgets.QLineEdit()
            self.i2 = QtWidgets.QLineEdit()

            formlayout.addRow(self.qlabel1, self.i1)
            formlayout.addRow(self.transport)
            formlayout.addRow(self.qlabel2, self.i2)

        elif selected == 'Bluetooth':
            pass

        self.formBox.setLayout(formlayout)
        self.mainLayout.addWidget(self.formBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.show()

    def validate_input(self):
        pass


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    baseapp = BaseApp(mainwindow=MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
