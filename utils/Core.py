from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy,\
    QFrame, QMenuBar, QMenu, QAction, QStatusBar, QErrorMessage,\
    QTabWidget, QHBoxLayout, QApplication, QMainWindow

from utils import CustomWidgets, Forms
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QRect, QMetaObject, QCoreApplication
from functools import partial
import logging
import PyCmdMessenger
import os
import json
import sys


class PyGUIno:
    def __init__(self):
        print("PyGUIno: Instantiating")
        self.app = QApplication(sys.argv)
        self.size = self.app.primaryScreen().size()
        self.pin_dict = None
        mainwindow = QMainWindow()
        self.tmp = mainwindow  # Shenanigan cause I don't want to refractor

        # Set up mainwindow, parameters
        mainwindow.resize(self.size.width(), self.size.height())
        mainwindow.setObjectName("PyGUIno")
        self.centralwidget = QWidget(mainwindow)
        mainwindow.setCentralWidget(self.centralwidget)
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.statusbar = QStatusBar(mainwindow)
        mainwindow.setStatusBar(self.statusbar)

        # Instantiate WidgetCoordinator
        self.widgetCoord = WidgetCoordinator(central_widget=self.centralwidget,
                                             comm_args=None, size=self.size, user_vars=None)

        # Set up menuBar
        self.menubar = QMenuBar(mainwindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        mainwindow.setMenuBar(self.menubar)

        self.menuFile = QMenu(self.menubar)
        self.menuConnection = QMenu(self.menuFile)
        self.menuBoards = QMenu(self.menuFile)
        self.menuTools = QMenu(self.menubar)
        self.menuLoggers = QMenu(self.menuTools)

        # Create all QActions
        self.actionNew = QAction(mainwindow)
        self.actionLoad = QAction(mainwindow)
        self.actionSerial = QAction(mainwindow)
        self.actionStop = QAction(mainwindow)
        self.actionBluetooth = QAction(mainwindow)
        self.actionIP = QAction(mainwindow)
        self.actionComm = QAction(mainwindow)
        self.actionI2C = QAction(mainwindow)
        self.actionSPI = QAction(mainwindow)
        self.actionTable = QAction(mainwindow)
        self.actionAddPlot = QAction(mainwindow)

        # Set up QAction triggers
        args1 = {'type': 'Serial', 'core': self.widgetCoord}
        self.actionSerial.triggered.connect(partial(self.set_connform, args=args1))
        args2 = {'type': 'WiFi', 'core': self.widgetCoord}
        self.actionIP.triggered.connect(partial(self.set_connform, args=args2))
        args3 = {'type': 'Bluetooth', 'core': self.widgetCoord}
        self.actionBluetooth.triggered.connect(partial(self.set_connform, args=args3))

        schemas = os.listdir("resources\\schemas")
        self.actionAddPlot.triggered.connect(self.ini_graph_dialog)

        for schema in schemas:
            fd = open("resources\\schemas\\"+schema, 'r')
            data = json.load(fd)
            qaction = QAction(mainwindow)
            qaction.setText(data['meta']['ui'])
            qaction.triggered.connect(partial(self.set_pin_dict, arg_data=data['pin']))
            self.menuBoards.addAction(qaction)
            fd.close()

        self.actionI2C.triggered.connect(partial(self.widgetCoord.create_logger_widget, log_id='I2C'))
        self.actionSPI.triggered.connect(partial(self.widgetCoord.create_logger_widget, log_id='SPI'))
        self.actionComm.triggered.connect(partial(self.widgetCoord.create_logger_widget, log_id='SERIAL'))

        self.actionTable.triggered.connect(self.widgetCoord.create_table_widget)

        # Add QAction to QMenu
        self.menuConnection.addAction(self.actionSerial)
        self.menuConnection.addAction(self.actionBluetooth)
        self.menuConnection.addAction(self.actionIP)

        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionStop)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuConnection.menuAction())
        self.menuFile.addAction(self.menuBoards.menuAction())
        self.menuLoggers.addAction(self.actionComm)
        self.menuLoggers.addAction(self.actionI2C)
        self.menuLoggers.addAction(self.actionSPI)
        self.menuTools.addAction(self.menuLoggers.menuAction())
        self.menuTools.addAction(self.actionAddPlot)
        self.menuTools.addAction(self.actionTable)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslate_ui(mainwindow)
        QMetaObject.connectSlotsByName(mainwindow)

        # Hacemos que actuen a los triggers para loggers

        print("BaseApp: Instanciado")

    def retranslate_ui(self, mainwindow):
        _translate = QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "Archivo"))
        self.menuConnection.setTitle(_translate("MainWindow", "Conexion"))
        self.menuBoards.setTitle(_translate("MainWindow", "Boards"))
        self.actionIP.setText(_translate("MainWindow", "IP"))
        self.menuTools.setTitle(_translate("MainWindow", "Herramientas"))
        self.menuLoggers.setTitle(_translate("MainWindow", "Loggers"))
        self.actionAddPlot.setText(_translate("MainWindow", "Graficas"))
        self.actionNew.setText(_translate("MainWindow", "Nuevo"))
        self.actionLoad.setText(_translate("MainWindow", "Cargar"))
        self.actionSerial.setText(_translate("MainWindow", "Serial"))
        self.actionBluetooth.setText(_translate("MainWindow", "Bluetooth"))
        self.actionComm.setText(_translate("MainWindow", "Comm"))
        self.actionI2C.setText(_translate("MainWindow", "I2C"))
        self.actionSPI.setText(_translate("MainWindow", "SPI"))
        self.actionTable.setText(_translate("MainWindow", "Tabla"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))

    def start(self):
        self.tmp.show()
        sys.exit(self.app.exec_())

    # Functions to trigger several menu actions
    def new_action(self):
        pass

    def load_action(self):
        pass

    def ini_graph_dialog(self):
        if self.pin_dict:
            print("BaseApp: Creating PlotForm")
            Forms.PlotForm(self.widgetCoord, self.pin_dict)
        else:
            error_msg = QErrorMessage()
            error_msg.showMessage("Please select a board first")
            error_msg.exec_()

    def set_pin_dict(self, arg_data):
        self.pin_dict = arg_data

    @staticmethod
    def set_connform(args):
        print('BaseApp: Creating ConnectionForm')
        Forms.ConnectionForm(args)


class WidgetCoordinator:
    def __init__(self, central_widget, comm_args, size, user_vars):
        print("WidgetCoordinator: Instantiating")
        # Class attributes
        width = size.width()
        height = size.height()
        self.list_widgets = []
        self.user_vars = dict()
        self.commands = [
            ["ack_start", "s"],  # To recieve: With this we will be aware when the communication has started
            ["request_pin", "i"],  # To send: First arg will be the number of pins to start tracking then the pin number
            ["arduino_transmit_pin_value", "ii"],  # To recieve: we recieve the pin and value
            ["request_debug_var_value", "iI"],  # To send: type of data and memory address
            ["answer_debug_var_value", "b*"],  # To recieve: the value as an bunch of bytes
            ["arduino_transmit_debug_var", "iIsb*"]   # To recieve: type of data, memory address, human identifier
            # and value as a bunch of bytes
        ]
        self.recv_thread = None
        self.comm = None
        # Start communication
        if comm_args:
            self.set_comm(comm_args=comm_args)
        if user_vars:
            self.user_vars = user_vars
        else:
            self.user_vars = dict()

        # Create loggers
        logs = ['I2C', 'SPI', 'SERIAL']
        for log_id in logs:
            log = logging.getLogger(log_id)
            log.setLevel(logging.INFO)

        # Create layout for the widgets
        q_plot = QFrame()
        q_logger = QFrame()
        q_table = QFrame()
        q_plot.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        q_logger.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        q_table.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        plt_container = QHBoxLayout()
        logger_container = QHBoxLayout()
        table_container = QHBoxLayout()

        self.PlotTabWidget = QTabWidget()
        self.PlotTabWidget.setFixedWidth(width/2)
        self.PlotTabWidget.setFixedHeight(height/2)
        self.LoggerTabWidget = QTabWidget()
        self.LoggerTabWidget.setFixedWidth(width/2)
        self.LoggerTabWidget.setFixedHeight(height/2)
        self.TableTabWidget = QTabWidget()

        plt_container.addWidget(self.PlotTabWidget)
        logger_container.addWidget(self.LoggerTabWidget)
        table_container.addWidget(self.TableTabWidget)

        q_plot.setLayout(plt_container)
        q_logger.setLayout(logger_container)
        q_table.setLayout(table_container)

        # self.PlotTabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mainLayout = QVBoxLayout(central_widget)
        upper_layout = QHBoxLayout()
        upper_layout.addWidget(q_plot)
        upper_layout.addWidget(q_logger)
        self.mainLayout.addLayout(upper_layout)
        self.mainLayout.addWidget(q_table)

    # Communication related methods
    def set_comm(self, comm_args):
        try:
            if comm_args['type'] == 'Serial':
                arduino = PyCmdMessenger.ArduinoBoard(comm_args['port'], comm_args['baudrate'],
                                                      timeout=3.0, settle_time=3.0)
                self.comm = PyCmdMessenger.CmdMessenger(arduino, self.commands)
            elif comm_args['type'] == 'WiFi':
                pass
            elif comm_args['type'] == 'Bluetooth':
                pass
            self.recv_thread = QThreadComm(self.comm)
            self.recv_thread.signal.connect(self.handle_new_data)
            self.recv_thread.start()
        except Exception as err:
            print(err.__class__)
            print(err)
            if self.recv_thread and self.recv_thread.isRunning():
                self.recv_thread.stop()

    def stop_comm(self):
        if self.recv_thread:
            self.recv_thread.stop()

    def handle_new_data(self, msg):
        input_log = logging.getLogger('SERIAL')
        input_log.info(msg)

        command = msg[0]
        payload = msg[1]
        ts = msg[2]

        if command == self.commands[0][0]:  # ack_start
            print("Communication started {}".format(payload))
        elif command == self.commands[2][0]:  # arduino_transmit_pin_value
            for widget in self.list_widgets:
                if isinstance(widget, CustomWidgets.WidgetPlot):
                    widget.new_data(data=payload, timestamp=ts)
        elif command == self.commands[5][0]:  # arduino_transmit_debug_var
            row_as_dict = dict()
            list_index = payload[0]
            type_list = [
                # TODO: check every data type properly works
                (self.comm._recv_bool, 'bool'),
                (self.comm._recv_byte, 'byte'),
                (self.comm._recv_char, 'char'),
                (self.comm._recv_float, 'float'),
                (self.comm._recv_double, 'double'),  # 8 in Arduino Due
                (self.comm._recv_int, 'int'),  # 4 on Due, Zero...
                (self.comm._recv_long, 'long'),
                (self.comm._recv_int, 'short'),
                (self.comm._recv_unsigned_int, 'unsigned int'),  # 4 on Due
                (self.comm._recv_unsigned_int, 'unsigned short'),
                (self.comm._recv_unsigned_long, 'unsigned long')
            ]
            # type of data, memory address, human identifier
            to_python_data = type_list[list_index][0]
            row_as_dict['data_type'] = type_list[list_index][1]
            row_as_dict['addr'] = payload[1]
            row_as_dict['name'] = payload[2]
            row_as_dict['value'] = to_python_data(bytes(payload[3:]))
            for widget in self.list_widgets:
                if isinstance(widget, CustomWidgets.UserVarsTable):
                    widget.new_arduino_data(row_as_dict)


    # Widget related methods
    def create_plot_widget(self, conf_ui, conf_plots):
        plot_widget = CustomWidgets.WidgetPlot(configuration_data=conf_ui,
                                               config_plt_data=conf_plots,
                                               user_dict_ref=self.user_vars)
        self.list_widgets.append(plot_widget)
        self.PlotTabWidget.addTab(plot_widget, conf_ui['title'])

    def create_logger_widget(self, log_id):
        log_widget = CustomWidgets.CustomLogger(log_id=log_id)
        self.list_widgets.append(log_widget)
        self.LoggerTabWidget.addTab(log_widget, log_id)

    def create_table_widget(self):
        # TODO: There won't be tabs for this, it's only temporal
        table_widget = CustomWidgets.UserVarsTable(self.user_vars)
        self.list_widgets.append(table_widget)
        self.TableTabWidget.addTab(table_widget, "")


class QThreadComm(QtCore.QThread):

    signal = pyqtSignal(tuple)  # Mandatory to be defined at level class

    def __init__(self, comm):
        QtCore.QThread.__init__(self, parent=None)
        self.comm = comm
        self.keep_going = True

    def run(self):
        while self.keep_going:
            try:
                msg = self.comm.receive()
                if msg:
                    self.signal.emit(msg)
            except Exception as err:
                print(err)

    def stop(self):
        self.keep_going = False