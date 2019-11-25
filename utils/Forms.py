from PyQt5 import QtWidgets, QtCore
from serial.tools.list_ports import comports
from functools import partial
import bluetooth
import re


class ConnectionForm(QtWidgets.QDialog):
    def __init__(self, args):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.selected = args['type']
        self.core = args['core']
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.dialogLayout = QtWidgets.QVBoxLayout()
        self.formBox = QtWidgets.QGroupBox(self.selected)
        formlayout = QtWidgets.QFormLayout()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Conexion")

        if self.selected == 'Serial':
            self.qlabel1 = QtWidgets.QLabel(self.formBox)
            self.qlabel2 = QtWidgets.QLabel(self.formBox)
            self.qlabel1.setText('Serial')
            self.qlabel2.setText('Baudrate')
            self.i1 = QtWidgets.QLineEdit()
            self.i2 = QtWidgets.QLineEdit()
            formlayout.addRow(self.qlabel1, self.i1)
            formlayout.addRow(self.qlabel2, self.i2)

        elif self.selected == 'Bluetooth':
            self.devices = dict()
            self.qlabel1 = QtWidgets.QLabel(self.formBox)
            self.qlabel1.setText("Devices: ")
            self.pick_bluetooth = QtWidgets.QComboBox()
            available_devices = bluetooth.discover_devices(duration=5, lookup_names=True)
            for addr, name in available_devices:
                self.devices[name] = addr
                self.pick_bluetooth.addItem(name)
            print(self.devices)
            formlayout.addRow(self.qlabel1, self.pick_bluetooth)

        elif self.selected == 'WiFi':
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

        self.formBox.setLayout(formlayout)
        self.mainLayout.addWidget(self.formBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.exec_()

    @QtCore.pyqtSlot()
    def accept(self):
        comm_args = {'type': self.selected}
        if self.selected == 'Serial':
            comm_args['port'] = self.i1.text()
            comm_args['baudrate'] = self.i2.text()

        elif self.selected == 'Bluetooth':
            name = self.pick_bluetooth.currentText()
            comm_args['mac_addr'] = self.devices[name]

        elif self.selected == 'WiFi':
            comm_args['ip'] = self.i1.text()
            comm_args['protocol'] = self.transport.currentText()
            comm_args['port'] = self.i2.text()

        if self.validate_input(comm_args):
            self.core.set_comm(comm_args)
        else:
            ErrorMessageWrapper('Connection Error', 'Error in the arguments')
        super().accept()

    @staticmethod
    def validate_input(comm_args):
        if comm_args['type'] == 'Serial':
            for (port, desc, hardware_id) in comports(include_links=False):
                if comm_args['port'] == port:
                    try:
                        int(comm_args['baudrate'])
                        return True
                    except ValueError:
                        return False
            return False

        # No need to check for bluetooth data
        elif comm_args['type'] == 'Bluetooth':
            return True
        elif comm_args['type'] == 'WiFi':
            valid_ip_address = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
            if re.match(valid_ip_address, comm_args['ip']):
                try:
                    port_number = int(comm_args['port'])
                    if 0 < port_number <= 65535:
                        return True
                except ValueError:
                    return False
            else:
                return False

        return False


# TODO: Support for debug vars too
class PlotForm(QtWidgets.QDialog):
    def __init__(self, core, pin_dict):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self._color_dict = {'r': 'red',
                            'g': 'green',
                            'b': 'blue',
                            'c': 'cyan',  # Unsure
                            'm': 'unknown2',
                            'y': 'yellow',
                            'k': 'black',
                            'w': 'white'}

        self.setWindowTitle("Add new plot")
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        self.coreRef = core

        # form Box
        formlayout = QtWidgets.QFormLayout()
        formbox = QtWidgets.QGroupBox("General settings")
        self.lineedit1 = QtWidgets.QLineEdit()
        qlabel1 = QtWidgets.QLabel('Title')
        formlayout.addRow(qlabel1, self.lineedit1)

        add_button = QtWidgets.QPushButton("Add")
        self.delete_button = QtWidgets.QPushButton("Delete")
        self.delete_button.setEnabled(False)

        # Attached functions to buttons

        self.pin_dict = pin_dict
        add_button.clicked.connect(self.on_click_add)

        button_container = QtWidgets.QHBoxLayout()
        button_container.addWidget(add_button)
        button_container.addWidget(self.delete_button)

        # A table to display the given data given on the dialog
        # created by the add_button
        self.qt_table = QtWidgets.QTableWidget()
        self.qt_table.setColumnCount(3)
        self.qt_table.setRowCount(0)
        self.qt_table.setHorizontalHeaderLabels(['Pins', 'Eval', 'Color'])
        self.qt_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.qt_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.qt_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.qt_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # ButtonBox
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

        # Adding everything to the vertical layout
        formbox.setLayout(formlayout)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(formbox)
        self.mainLayout.addLayout(button_container)
        self.mainLayout.addWidget(self.qt_table)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

        # Show the form
        self.exec_()

    def on_click_add(self):
        # open a PinEvalDialog
        PinEvalDialog(self, pin_dict=self.pin_dict, color_dict=self._color_dict)

    def add_new_row(self, pin_selected, eval_string, color):
        self.delete_button.setEnabled(True)
        append_row = self.qt_table.rowCount()
        self.qt_table.insertRow(append_row)
        item_pin = QtWidgets.QTableWidgetItem(pin_selected)
        item_math = QtWidgets.QTableWidgetItem(eval_string)
        item_color = QtWidgets.QTableWidgetItem(color)
        self.qt_table.setItem(append_row, 0, item_pin)
        self.qt_table.setItem(append_row, 1, item_math)
        self.qt_table.setItem(append_row, 2, item_color)

    def accept(self):
        try:
            n_rows = self.qt_table.rowCount()
            conf_plt_pins = []
            for current_row in range(0, n_rows):
                item_pin = self.qt_table.item(current_row, 0)
                item_math = self.qt_table.item(current_row, 1)
                item_color = self.qt_table.item(current_row, 2)

                if item_pin and item_math and item_color:
                    pin_key = item_pin.text()
                    pin_number = self.pin_dict[pin_key]
                    math_expression = item_math.text()
                    color_val = item_color.text()
                    color_key = list(self._color_dict.keys())[list(self._color_dict.values()).index(color_val)]
                    conf_plt_pins.append((pin_key, pin_number, math_expression, color_key))

            # Call the core to instantiate the PlotWidget
            general_config = dict()
            general_config['title'] = self.lineedit1.text()
            self.coreRef.create_plot_widget(general_config, conf_plt_pins)
        except Exception as err:
            print(err)
        finally:
            super().accept()


class PinEvalDialog(QtWidgets.QDialog):
    def __init__(self, form_to_notify, pin_dict, color_dict):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(" ")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        qlabel1 = QtWidgets.QLabel("Pin:")
        qlabel2 = QtWidgets.QLabel("Expression to value:")
        qlabel3 = QtWidgets.QLabel("Plot Color:")

        self.pin_selector = QtWidgets.QComboBox()
        for pin_id in sorted(pin_dict.keys()):
            self.pin_selector.addItem(str(pin_id))
        self.to_evaluate = QtWidgets.QLineEdit()
        self.pick_color = QtWidgets.QComboBox()
        for color in sorted(color_dict.values()):
            self.pick_color.addItem(color)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(partial(self.custom_accept, form_to_notify=form_to_notify))

        main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(qlabel1, self.pin_selector)
        form_layout.addRow(qlabel2, self.to_evaluate)
        form_layout.addRow(qlabel3, self.pick_color)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.exec_()

    def custom_accept(self, form_to_notify):
        # Get the user input and give it to form_to_notify
        pin_selected = self.pin_selector.currentText()
        eval_string = self.to_evaluate.text()
        color_selected = self.pick_color.currentText()

        # Handle adquired data to the PlotForm object
        form_to_notify.add_new_row(pin_selected, eval_string, color_selected)
        super().accept()


class ErrorMessageWrapper:
    # A singleton approach to avoid bombing the user with
    # error windows
    instance = None

    def __init__(self, err_title, err_str):
        if not ErrorMessageWrapper.instance:
            ErrorMessageWrapper.instance = ErrorMessageWrapper.ErrorMessage(err_title, err_str)

    class ErrorMessage(QtWidgets.QErrorMessage):
        def __init__(self, err_title, err_str):
            QtWidgets.QErrorMessage.__init__(self)
            self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
            self.setWindowTitle(err_title)
            self.showMessage(err_str)
            self.exec_()
