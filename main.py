import os, json
from PyQt5 import QtCore, QtGui, QtWidgets
from utils.CustomWidgets import WidgetPlot
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

        # Hacemos que actuen a los triggers

        # Añadimos lo QAction al menu boards
        schemas = os.listdir("resources\\schemas")

        for schema in schemas:
            print("Opening {}".format(schema))
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

        # Pruebas
#        self.pruebaPlot = None
#        self.test()

    # def test(self):
        # self.pruebaPlot = WidgetPlot()
        # self.pruebaPlot.setObjectName("plot")
        # self.gridLayoutWidget.addWidget(self.pruebaPlot, 0, 0, 1, 1)

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
        print(arg_data)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    baseapp = BaseApp(mainwindow=MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
