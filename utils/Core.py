from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy,\
    QFileDialog, QToolBar, QAction, QStatusBar, QTabWidget, \
    QHBoxLayout, QApplication, QMainWindow, QComboBox, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from utils import CustomWidgets, Forms, Communication

import logging
import PyCmdMessenger
import os
import json
import sys


class PyGUIno:
    def __init__(self):
        # Set up all the window related stuff
        self._app = QApplication(sys.argv)
        self._window = QMainWindow()
        size = self._app.primaryScreen().size()
        self._window.resize(int(size.width()*0.7),
                            int(size.height()*0.8))
        self._window.setObjectName("PyGUIno")
        self._window.setWindowTitle('PyGUIno')
        self._window.setWindowIcon(QIcon('resources\\assets\\etsi.png'))
        self._centralwidget = QWidget(self._window)
        self._window.setCentralWidget(self._centralwidget)
        self._centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QHBoxLayout()
        self._centralwidget.setLayout(self.layout)

        # Create the toolbar and the actions
        self.toolbar = QToolBar()
        save_action = QAction(QIcon('resources\\assets\\ic_save_3x.png'), 'Guardar', self._window)
        save_action.setStatusTip('Guarda la configuración de las gráficas actuales')
        load_action = QAction(QIcon('resources\\assets\\ic_open_in_new_18pt_3x.png'), 'Cargar', self._window)
        load_action.setStatusTip('Cargar la configuración de gráficas')
        self.connect_menu = QAction(QIcon('resources\\assets\\ic_settings_black_48dp.png'), 'Conectar', self._window)
        self.connect_menu.setStatusTip('Configuración de la conexión a Arduino')
        self.start_action = QAction(QIcon('resources\\assets\\ic_play_arrow_3x.png'), 'Comenzar', self._window)
        self.start_action.setEnabled(False)
        self.start_action.setStatusTip('Comienza la conexión con Arduino')
        self.stop_action = QAction(QIcon('resources\\assets\\ic_stop_3x.png'), 'Detener', self._window)
        self.stop_action.setEnabled(False)
        self.stop_action.setStatusTip('Detiene la conexión con Arduino')

        add_plot = QAction(QIcon('resources\\assets\\ic_timeline_48pt_3x.png'), 'Añadir gráfica', self._window)
        add_plot.setStatusTip('Añadir gráfica')

        board_selector = QComboBox()
        self.pin_dict = None
        self._pin_choices = []
        self.data_size = []
        schemas = os.listdir("resources\\schemas")

        for schema in schemas:
            fd = open("resources\\schemas\\" + schema, 'r')
            data = json.load(fd)
            board_selector.addItem(data['name'])
            tmp = dict()

            # añadir al dict los pines digitales
            for x in range(0, data['digital']):
                tmp[str(x)] = x
                pass

            # añadir al dict los pines analogicos
            for x in range(data['digital'], data['digital'] + data['analog']):
                tmp["A"+str(x-data['digital'])] = x

            # Debe añadir un dictionary a la lista
            self._pin_choices.append(tmp)
            self.data_size.append(data["data_size"])
            self.pin_dict = tmp
            fd.close()

        # Signal handlers
        save_action.triggered.connect(self.save)
        load_action.triggered.connect(self.load)
        add_plot.triggered.connect(self.ini_graph_dialog)
        self.connect_menu.triggered.connect(self.comm_config)
        self.start_action.triggered.connect(self.start)
        self.stop_action.triggered.connect(self.stop)
        board_selector.currentIndexChanged.connect(self.switch_board)

        self.toolbar.addAction(save_action)
        self.toolbar.addAction(load_action)
        self.toolbar.addAction(add_plot)
        self.toolbar.addAction(self.connect_menu)
        self.toolbar.addAction(self.start_action)
        self.toolbar.addAction(self.stop_action)
        self.toolbar.addWidget(board_selector)

        self._window.addToolBar(self.toolbar)

        # Create status bar
        self.statusbar = QStatusBar(self._window)
        self._window.setStatusBar(self.statusbar)

        # Create Workspace area
        self.widgetCoord = WidgetCoordinator()
        self.widgetCoord.data_size = self.data_size[-1]

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

    def start_pygu(self):
        self._window.show()
        sys.exit(self._app.exec_())

    # Functions to trigger several menu actions
    def save(self):
        try:
            some_tuple = QFileDialog.getSaveFileName(parent=None, caption='Guardar',
                                                     directory='')
            abs_path = some_tuple[0]
            file = open(abs_path, 'w')
            data_to_save = json.dumps(self.widgetCoord.save(), sort_keys=True,
                                      indent=4, separators=(',', ': '))
            print(data_to_save)
            file.write(data_to_save)
            file.close()
        except Exception as e:
            print(e)

    def load(self):
        try:
            some_tuple = QFileDialog().getOpenFileName(parent=None, caption='Cargar',
                                                       directory='')
            abs_path = some_tuple[0]
            file = open(abs_path, 'r')
            content = json.load(file)
            self.widgetCoord.load(content)
            file.close()
        except Exception as e:
            print(e)

    def comm_config(self):
        Forms.ConnectionForm(self.connect_menu, self.start_action, self.stop_action,
                             self.widgetCoord)

    def stop(self):
        self.widgetCoord.stop_comm()
        self.connect_menu.setEnabled(True)
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(False)

    def start(self):
        self.widgetCoord.start_comm()
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)

    def ini_graph_dialog(self):
        Forms.PlotForm(self.widgetCoord, self.pin_dict,
                       self.widgetCoord.debug_vars)

    def switch_board(self, index):
        self.pin_dict = self._pin_choices[index]
        self.widgetCoord.data_size = self.data_size[index]


class WidgetCoordinator:
    def __init__(self):
        # Class attributes
        self.plt_list = []
        self.data_size = None
        self.user_vars = dict()
        self.debug_vars = dict()
        self.commands = [
            ["ack_start", "s"],  # To recieve: With this we will be aware when the communication has started
            ["request_pin", "i"],  # To send: First arg will be the number of pins to start tracking then the pin number
            ["arduino_transmit_pin_value", "ii"],  # To recieve: we recieve the pin and value
            ["request_debug_var_value", "iI"],  # To send: type of data and memory address
            ["answer_debug_var_value", "b*"],  # To recieve: the value as an bunch of bytes
            ["arduino_transmit_debug_var", "iIsb*"],  # To recieve: type of data, memory address, human identifier
                                                      # and value as a bunch of bytes
            ["arduino_byte_read", "Ib"],  # I2C: Arduino sends read data from an addr
            ["arduino_byte_write", "Ib*"],  # I2C: Arduino sends writen data from an addr
            ["arduino_spi_transmit", "II"]  # SPI: Transmited value then recieved value
        ]
        self.arduino = None
        self.comm = None
        self.recv_thread = None

        # Create the widgets
        self.debug_vars_widget = CustomWidgets.DebugVarsTable(debug_vars=self.debug_vars)
        self.user_vars_table = CustomWidgets.UserVarsTable(user_vars=self.user_vars)
        self.plot_container = QTabWidget()
        self.plot_container.setMinimumWidth(400)
        self.plot_container.setMinimumHeight(300)
        self.log_container = QTabWidget()
        self.plot_container.setStyleSheet('background-color:white')
        self.log_container.setStyleSheet('background-color:white')
        # Create loggers
        logs = ['Todos', 'I2C', 'SPI']
        for log_id in logs:
            log = logging.getLogger(log_id)
            log.setLevel(logging.INFO)
            self.create_logger_widget(log_id)

    # Communication related methods
    def set_comm(self, comm_args):
        try:
            if comm_args['type'] == 'Serial':
                self.arduino = PyCmdMessenger.ArduinoBoard(comm_args['port'], comm_args['baudrate'],
                                                           timeout=3.0, settle_time=3.0,
                                                           int_bytes=self.data_size['int_bytes'],
                                                           float_bytes=self.data_size['float_bytes'],
                                                           double_bytes=self.data_size['double_bytes'],
                                                           long_bytes=self.data_size['long_bytes'])
                self.comm = PyCmdMessenger.CmdMessenger(self.arduino, self.commands)
            elif comm_args['type'] == 'WiFi':
                pass
            elif comm_args['type'] == 'Bluetooth':
                self.arduino = Communication.ArduinoBoardBluetooth(mac_addr=comm_args['mac_addr'],
                                                                   int_bytes=self.data_size['int_bytes'],
                                                                   float_bytes=self.data_size['float_bytes'],
                                                                   double_bytes=self.data_size['double_bytes'],
                                                                   long_bytes=self.data_size['long_bytes'])
                self.comm = PyCmdMessenger.CmdMessenger(self.arduino, self.commands)
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
        if self.comm:
            self.recv_thread = QThreadComm(self.comm)
            self.recv_thread.signal.connect(self.handle_new_data)
            self.recv_thread.start()
        else:
            Forms.ErrorMessageWrapper('Connection Error', 'There was an error setting up the connection')

    def handle_new_data(self, msg):
        try:

            command = msg[0]
            payload = msg[1]
            ts = msg[2]

            input_log = logging.getLogger('Todos')
            input_log.info("[{:5.3f}] | {} | {} ".format(ts, command, payload))

            # only arduino_byte_read, arduino_byte_write y arduino_spi_transmit
            # needs to be send to the SPI and
            if command == "arduino_byte_read":
                text = "Read from {} | Value: {}".format(payload[0], hex(payload[1]))
                input_log = logging.getLogger('I2C')
                input_log.info(text)

            elif command == "arduino_byte_write":
                if type(payload) == type([]):
                    payload.pop(0)
                    hex_payload = []
                    for x in payload:
                        hex_payload.append(hex(x))
                    text = "Writing value: {}".format(hex_payload)
                else:
                    text = "Writing value: {}".format(hex(payload))
                input_log = logging.getLogger('I2C')
                input_log.info(text)

            elif command == "arduino_spi_transmit":
                text = "Tx value: 0x{:02X} | SPDR value: 0x{:02X}".format(payload[0], payload[1])
                input_log = logging.getLogger('SPI')
                input_log.info(text)

            elif command == self.commands[0][0]:  # ack_start
                print("Comunicación establecida {}".format(payload))

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
                    Forms.ErrorMessageWrapper('Error en variable de depuración',
                                              'Ha habido un error en relacionado '
                                              'con variables de depuracion\n{}'.format(err))
        except Exception as e:
            print(e)
            Forms.ErrorMessageWrapper(e.__class__, e)

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

    # Load and save related methods
    def save(self):
        save_dict = dict()
        return_list = list()

        for widgetPlot in self.plt_list:
            return_list.append(widgetPlot.serialize())
        save_dict['user_dict'] = self.user_vars
        save_dict['widget_plot_list'] = return_list

        print('-----------------------------')
        print(save_dict)
        print('-----------------------------')

        return save_dict

    def load(self, content):
        # Primero user_dict
        user_dict = content['user_dict']
        for key in user_dict.keys():
            self.user_vars_table.add_to_user_vars(key, user_dict[key])

        # Ahora debemos crear los WidgetPlot
        for widgetPlot in content['widget_plot_list']:
            # Preparamos los pltAux que contendra
            conf_plots = list()
            for plt_aux in widgetPlot['pltAux_list']:
                conf_plots.append((plt_aux['pin_key'], plt_aux['pin'],
                                  plt_aux['math_expression'], plt_aux['color']))
            # Preparamos el conf_ui
            conf_ui = dict()
            conf_ui['title'] = widgetPlot['title']
            self.create_plot_widget(conf_ui=conf_ui, conf_plots=conf_plots)


class QThreadComm(QThread):

    signal = pyqtSignal(tuple)  # Mandatory to be defined at level class

    def __init__(self, comm):
        QThread.__init__(self, parent=None)
        self.comm = comm
        self.keep_running = True

    def run(self):
        msg = None
        while self.keep_running:
            try:
                msg = self.comm.receive()
                if msg:
                    self.signal.emit(msg)
            except Exception as err:
                print('Error en la recepción de msg')
                if msg:
                    print(msg)
                print(err)

    def stop(self):
        self.keep_running = False
