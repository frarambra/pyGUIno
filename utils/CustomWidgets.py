from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, \
    QPushButton, QSizePolicy, QGridLayout, QMenuBar, QMenu, QAction, QStatusBar, QErrorMessage
from PyQt5.QtCore import pyqtSlot, QTimer, QRect, QMetaObject, QCoreApplication
from functools import partial
from utils import Forms, Core

import pyqtgraph as pg
import time
import logging
import json
import os


class BaseApp:
    def __init__(self, mainwindow):
        print("BaseApp: Instantiating")
        self.pin_list = []
        mainwindow.resize(800, 600)
        mainwindow.setObjectName("MainWindow")
        self.centralwidget = QWidget(mainwindow)
        mainwindow.setCentralWidget(self.centralwidget)
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gridLayoutWidget = QGridLayout(self.centralwidget)
        self.core = Core.Core(layout=self.gridLayoutWidget, comm_args=None)

        self.menubar = QMenuBar(mainwindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))

        self.menuArchivo = QMenu(self.menubar)
        self.menuConexion = QMenu(self.menuArchivo)
        self.connForm = None
        self.menuBoards = QMenu(self.menuArchivo)

        self.menuHerramientas = QMenu(self.menubar)
        self.menuLoggers = QMenu(self.menuHerramientas)

        mainwindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainwindow)
        mainwindow.setStatusBar(self.statusbar)

        # Instanciamos los QAction
        self.actionNuevo = QAction(mainwindow)
        self.actionCargar = QAction(mainwindow)
        self.actionSerial = QAction(mainwindow)
        self.actionStop = QAction(mainwindow)
        self.actionBluetooth = QAction(mainwindow)
        self.actionIP = QAction(mainwindow)
        self.actionComm = QAction(mainwindow)
        self.actionI2C = QAction(mainwindow)
        self.actionSPI = QAction(mainwindow)
        self.actionTabla = QAction(mainwindow)
        self.actionGrafica = QAction(mainwindow)

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
            qaction = QAction(mainwindow)
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
        self.menuArchivo.addAction(self.actionStop)
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
        QMetaObject.connectSlotsByName(mainwindow)

        # Hacemos que actuen a los triggers para loggers
        self.actionI2C.triggered.connect(partial(self.core.create_logger_widget, log_id='I2C'))
        self.actionSPI.triggered.connect(partial(self.core.create_logger_widget, log_id='SPI'))
        self.actionComm.triggered.connect(partial(self.core.create_logger_widget, log_id='SERIAL'))

        print("BaseApp: Instanciado")

    def retranslate_ui(self, mainwindow):
        _translate = QCoreApplication.translate
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
        self.actionStop.setText(_translate("MainWindow", "Stop"))

    def ini_graph_dialog(self):
        if self.pin_list:
            print("BaseApp: Creating PlotForm")
            Forms.PlotForm(self.core, self.pin_list)
        else:
            error_msg = QErrorMessage()
            error_msg.showMessage("Please select a board first")
            error_msg.exec_()

    def set_pin_list(self, arg_data):
        self.pin_list = arg_data

    def set_connform(self, args):
        print('BaseApp: Creating ConnectionForm')
        self.connForm = Forms.ConnectionForm(args)


class WidgetPlot(QWidget):
    def __init__(self, meta, pin_and_eval):
        QWidget.__init__(self)
        # haria falta un formulario para escoger la posicion en el grid o bastaria con un "drag and drop"
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setLayout(QVBoxLayout())
        self.plot_widget = pg.PlotWidget(background='w')
        self.layout().addWidget(self.plot_widget)

        self.contained_plots = []
        self.t_ini = time.time()
        # Set title and such from "meta"

        for tmp in pin_and_eval:
            plt_item = self.plot_widget.getPlotItem()
            plt_aux_tmp = self.PltAux(pin=tmp[0], plt_item=plt_item)
            self.contained_plots.append(plt_aux_tmp)

    def new_data(self, data, timestamp):
        pin = data[0]
        value = data[1]
        print('WidgetPlot: {}'.format(self.contained_plots))

        for plt_aux in self.contained_plots:
            print('WidgetPlot: Pin->{}'.format(plt_aux.pin))
            if plt_aux.pin == str(pin):
                print('WidgetPlot: begin update for {}'.format(plt_aux))
                plt_aux.update(timestamp-self.t_ini, value)
                print("time_axe:  {}".format(plt_aux.time_axe))
                print("value_axe:  {}".format(plt_aux.value_axe))

    # TODO: Implement evaluation function with either exec or eval
    class PltAux:
        def __init__(self, pin, plt_item):
            # Length must match
            self.limit = 100
            self.pin = pin
            self.plt_item = plt_item
            self.time_axe = []
            self.value_axe = []

        def update(self, ts, value):
            self.shift(ts, value)
            self.plt_item.plot(self.time_axe, self.value_axe)

        def shift(self, ts, value):
            if len(self.time_axe) >= self.limit:
                self.time_axe.pop(0)
                self.value_axe.pop(0)
            self.time_axe.append(ts)
            self.value_axe.append(value)


'''
    Las siguiente clase tiene como objetivo crear un logger funcional con el 
    objetivo de poder mostrar informacion de cualquier tipo, ya sea lo que pase por el serial
    o algun protocolo especifico
'''


class CustomLogger(QWidget, logging.Handler):
    def __init__(self, log_id):
        QWidget.__init__(self)
        self.needed_resources = []

        logging.Handler.__init__(self)
        self.log = logging.getLogger(log_id)
        self.log.addHandler(self)

        base = QVBoxLayout()
        self.setLayout(base)

        # Configuramos donde ira el texto del logger
        self.loggerText = QPlainTextEdit()
        self.loggerText.setReadOnly(True)
        self.loggerText.setFixedHeight(300)
        self.loggerText.setFixedWidth(300)

        # Miscelanea
        self.title = QLabel()
        self.title.setText(log_id+" Logger")
        self.button = QPushButton()
        self.button.clicked.connect(self.click_event)
        self.button.setText('Cerrar')

        # Añadimos todas las cosas para que quede bonito
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.loggerText)

    def emit(self, record):
        msg = 'Contenido del mensaje:\n{}'.format(self.format(record))
        print(msg)
        self.loggerText.appendPlainText(msg)

    # TODO: Borrar esto, solo es temporal
    @pyqtSlot()
    def click_event(self):
        print('click_event ejecutado')
        text = 'Prueba a las {}'.format(time.time())
        self.log.info(text)




