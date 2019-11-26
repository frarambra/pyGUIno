from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy,\
    QFrame, QToolBar, QTextEdit, QAction, QStatusBar, QErrorMessage,\
    QTabWidget, QHBoxLayout, QApplication, QMainWindow, QComboBox, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QMetaObject, QCoreApplication, QThread
from PyQt5.QtGui import QIcon
from functools import partial
from utils import CustomWidgets, Forms, Communication

import logging
import PyCmdMessenger
import os
import json
import sys


class PyGUIno:
    def __init__(self):
        # Set up all the window related stuff
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        size = self.app.primaryScreen().size()
        self.window.resize(int(size.width()*0.7),
                           int(size.height()*0.8))
        self.window.setObjectName("PyGUIno")
        self.window.setWindowTitle('PyGUIno')
        self.window.setWindowIcon(QIcon('resources\\assets\\roto2.png'))
        self.centralwidget = QWidget(self.window)
        self.window.setCentralWidget(self.centralwidget)
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QHBoxLayout()
        self.centralwidget.setLayout(self.layout)

        # Create actions and then toolbar
        # TODO: add aligment
        self.toolbar = QToolBar()
        save_action = QAction(QIcon('resources\\assets\\roto2.png'), 'Save', self.window)
        save_action.setStatusTip('Save current currents plots')
        load_action = QAction(QIcon('resources\\assets\\roto2.png'), 'Load', self.window)
        load_action.setStatusTip('Load plots from other projects')
        self.connect_action = QAction(QIcon('resources\\assets\\roto2.png'), 'Connect', self.window)
        self.connect_action.setStatusTip('Configure the connection to Arduino')
        self.disconnect_action = QAction(QIcon('resources\\assets\\roto2.png'), 'Start', self.window)
        self.disconnect_action.setEnabled(False)
        self.disconnect_action.setStatusTip('Stops the Connection with Arduino')
        add_plot = QAction(QIcon('resources\\assets\\roto2.png'), 'Add plot', self.window)
        add_plot.setStatusTip('Adds a plot')

        board_selector = QComboBox()
        self.pin_dict = None
        self._pin_choices = []
        schemas = os.listdir("resources\\schemas")
        for schema in schemas:
            fd = open("resources\\schemas\\" + schema, 'r')
            data = json.load(fd)
            board_selector.addItem(data['meta']['ui'])
            # Set default pin_dict to avoid None errors
            self._pin_choices.append(data['pin'])
            self.pin_dict = data['pin']
            fd.close()

        # Signal handlers
        save_action.triggered.connect(self.save)
        load_action.triggered.connect(self.load)
        add_plot.triggered.connect(self.ini_graph_dialog)
        self.connect_action.triggered.connect(self.connect)
        self.disconnect_action.triggered.connect(self.stop)
        board_selector.currentIndexChanged.connect(self.switch_board)

        self.toolbar.addAction(save_action)
        self.toolbar.addAction(load_action)
        self.toolbar.addAction(add_plot)
        self.toolbar.addAction(self.connect_action)
        self.toolbar.addAction(self.disconnect_action)
        self.toolbar.addWidget(board_selector)

        self.window.addToolBar(self.toolbar)

        # Create status bar
        self.statusbar = QStatusBar(self.window)
        self.window.setStatusBar(self.statusbar)

        # Create Workspace area
        self.widgetCoord = WidgetCoordinator()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        top_left_side = self.widgetCoord.plot_container
        top_right_side = self.widgetCoord.user_vars_table
        low_left_side = self.widgetCoord.debug_vars_widget
        low_right_side = self.widgetCoord.log_container

        # Prepare horizontal splitter and left and right vertical splitters
        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.setStyleSheet('background-color:rgb(239, 239, 239)')
        left_vertical_splitter = QSplitter(Qt.Vertical)
        left_vertical_splitter.setStyleSheet('background-color:rgb(239, 239, 239)')
        right_vertical_splitter = QSplitter(Qt.Vertical)
        right_vertical_splitter.setStyleSheet('background-color:rgb(239, 239, 239)')

        # First add left then add right
        left_vertical_splitter.addWidget(top_left_side)
        left_vertical_splitter.addWidget(low_left_side)
        left_layout.addWidget(left_vertical_splitter)

        # The same but on the right side
        right_vertical_splitter.addWidget(top_right_side)
        right_vertical_splitter.addWidget(low_right_side)
        right_layout.addWidget(right_vertical_splitter)

        # Finally add the vertical splitters to the horizontal splitter
        # And add it to the horizontal layout
        horizontal_splitter.addWidget(left_vertical_splitter)
        horizontal_splitter.addWidget(right_vertical_splitter)
        self.layout.addWidget(horizontal_splitter)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def start(self):
        self.window.show()
        sys.exit(self.app.exec_())

    # Functions to trigger several menu actions
    def save(self):
        pass

    def load(self):
        pass

    def connect(self):
        Forms.ConnectionForm(self.connect_action, self.disconnect_action,
                             self.widgetCoord)

    def stop(self):
        self.widgetCoord.stop_comm()
        self.disconnect_action.setEnabled(False)
        self.connect_action.setEnabled(True)

    def ini_graph_dialog(self):
        Forms.PlotForm(self.widgetCoord, self.pin_dict,
                       self.widgetCoord.debug_vars)

    def switch_board(self, index):
        self.pin_dict = self._pin_choices[index]


class WidgetCoordinator:
    def __init__(self):
        # Class attributes
        self.plt_list = []
        self.user_vars = dict()
        self.debug_vars = dict()
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

        # Create layout for the widgets
        self.debug_vars_widget = CustomWidgets.DebugVarsTable(debug_vars=self.debug_vars)
        self.user_vars_table = CustomWidgets.UserVarsTable(user_vars=self.user_vars)
        self.plot_container = QTabWidget()
        self.plot_container.setMinimumWidth(400)
        self.plot_container.setMinimumHeight(300)
        self.log_container = QTabWidget()
        self.plot_container.setStyleSheet('background-color:white')
        self.log_container.setStyleSheet('background-color:white')
        # Create loggers
        logs = ['All', 'Serial', 'I2C', 'SPI']
        for log_id in logs:
            log = logging.getLogger(log_id)
            log.setLevel(logging.INFO)
            self.create_logger_widget(log_id)

    # Communication related methods
    def set_comm(self, comm_args):
        try:
            print('Starting communication')
            print('comm_args: {}'.format(comm_args))
            if comm_args['type'] == 'Serial':
                arduino = PyCmdMessenger.ArduinoBoard(comm_args['port'], comm_args['baudrate'],
                                                      timeout=3.0, settle_time=3.0)
                self.comm = PyCmdMessenger.CmdMessenger(arduino, self.commands)
            elif comm_args['type'] == 'WiFi':
                pass
            elif comm_args['type'] == 'Bluetooth':
                arduino = Communication.ArduinoBoardBluetooth(mac_addr=comm_args['mac_addr'])
                self.comm = PyCmdMessenger.CmdMessenger(arduino, self.commands)
        except Exception as err:
            print(err.__class__)
            print(err)
            if self.recv_thread and self.recv_thread.isRunning():
                self.recv_thread.stop()
            return False
        else:
            return True

    def stop_comm(self):
        if self.recv_thread:
            self.recv_thread.stop()
        self.comm.board.close()
        self.comm = None  # To force the garbage collector

    def start_comm(self):
        self.recv_thread = QThreadComm(self.comm)
        self.recv_thread.signal.connect(self.handle_new_data)
        self.recv_thread.start()

    def handle_new_data(self, msg):
        input_log = logging.getLogger('All')
        input_log.info(msg)

        command = msg[0]
        payload = msg[1]
        ts = msg[2]

        if command == self.commands[0][0]:  # ack_start
            print("Communication started {}".format(payload))
        elif command == self.commands[2][0]:  # arduino_transmit_pin_value
            for widget in self.plt_list:
                if isinstance(widget, CustomWidgets.WidgetPlot):
                    widget.new_data(data=payload, timestamp=ts)
        elif command == self.commands[5][0]:  # arduino_transmit_debug_var
            row_as_dict = dict()
            list_index = payload[0]
            type_list = [
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
            try:
                to_python_data = type_list[list_index][0]
                row_as_dict['data_type'] = type_list[list_index][1]
                row_as_dict['addr'] = payload[1]
                row_as_dict['name'] = payload[2]
                row_as_dict['value'] = to_python_data(bytes(payload[3:]))
                self.debug_vars_widget.new_arduino_data(row_as_dict)
                for widget in self.plt_list:
                    if isinstance(widget, CustomWidgets.UserVarsTable):
                        widget.new_arduino_data(row_as_dict)
            except Exception as err:
                Forms.ErrorMessageWrapper('Debug Variable Error',
                                          'There was an error related to debug variables\n{}'.format(err))

    # Widget related methods
    def create_plot_widget(self, conf_ui, conf_plots):
        plot_widget = CustomWidgets.WidgetPlot(configuration_data=conf_ui,
                                               config_plt_data=conf_plots,
                                               user_dict_ref=self.user_vars)
        self.plt_list.append(plot_widget)
        self.plot_container.addTab(plot_widget, conf_ui['title'])

    def create_logger_widget(self, log_id):
        log_widget = CustomWidgets.CustomLogger(log_id=log_id)
        self.log_container.addTab(log_widget, log_id)


class QThreadComm(QThread):

    signal = pyqtSignal(tuple)  # Mandatory to be defined at level class

    def __init__(self, comm):
        QThread.__init__(self, parent=None)
        self.comm = comm
        self.keep_going = True

    def run(self):
        msg = None
        while self.keep_going:
            try:
                msg = self.comm.receive()
                if msg:
                    self.signal.emit(msg)
            except Exception as err:
                print('Error while handling msg')
                if msg:
                    print(msg)
                print(err)

    def stop(self):
        self.keep_going = False
