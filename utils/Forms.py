from PyQt5 import QtWidgets, QtCore
from serial.tools.list_ports import comports
import bluetooth
import re


class ConnectionForm(QtWidgets.QDialog):
    # TODO: Remove try catch
    def __init__(self, menu_action, start_action, stop_action, widget_coord):
        try:
            QtWidgets.QDialog.__init__(self)
            self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
            self.widgetCoord = widget_coord
            self.stop_action = stop_action
            self.menu_action = menu_action
            self.start_action = start_action
            self.selected = 'Serial'  # Default value
            self.devices = dict()  # Just used on bluetooth connections

            # Select type of connection
            conn_selection_layout = QtWidgets.QHBoxLayout()
            serial_button = QtWidgets.QRadioButton('Serial')
            serial_button.setChecked(True)
            bluetooth_button = QtWidgets.QRadioButton('Bluetooth')
            # internet_button = QtWidgets.QRadioButton('Internet')
            serial_button.toggled.connect(self.on_selected)
            bluetooth_button.toggled.connect(self.on_selected)
            # internet_button.toggled.connect(self.on_selected)
            conn_selection_layout.addWidget(serial_button)
            conn_selection_layout.addWidget(bluetooth_button)
            # conn_selection_layout.addWidget(internet_button)

            # Middle section for the type of connection
            self.formBox = QtWidgets.QGroupBox()
            self.qlabel1 = QtWidgets.QLabel(self.formBox)
            self.qlabel2 = QtWidgets.QLabel(self.formBox)
            self.i1 = QtWidgets.QLineEdit()
            self.i2 = QtWidgets.QLineEdit()
            self.transport = QtWidgets.QComboBox()
            self.pick_bluetooth = QtWidgets.QComboBox()

            # Accept/Reject
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            button_box.rejected.connect(self.reject)
            button_box.accepted.connect(self.accept)

            # Add everything to the dialog layout
            self.formlayout = QtWidgets.QFormLayout()
            main_layout = QtWidgets.QVBoxLayout()
            self.setWindowTitle("Configurar conexión")
            self.formBox.setLayout(self.formlayout)
            main_layout.addLayout(conn_selection_layout)
            main_layout.addWidget(self.formBox)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)

            self.formBox.setTitle('Serial')
            self.qlabel1.setText('Puerto')
            self.qlabel2.setText('Tasa de baudios')
            self.formlayout.addRow(self.qlabel1, self.i1)
            self.formlayout.addRow(self.qlabel2, self.i2)

            self.exec_()
        except Exception as err:
            print(err)

    def on_selected(self):
        try:
            selected_button = self.sender()
            self.selected = selected_button.text()
            # Delete in formlayout
            while self.formlayout.count():
                item = self.formlayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Now that the formLayout is empty we populate it
            self.formBox.setTitle(self.selected)
            if self.selected == 'Serial':
                self.qlabel1 = QtWidgets.QLabel(self.formBox)
                self.qlabel2 = QtWidgets.QLabel(self.formBox)
                self.qlabel1.setText('Port')
                self.qlabel2.setText('Baudrate')
                self.i1 = QtWidgets.QLineEdit()
                self.i2 = QtWidgets.QLineEdit()

                self.formlayout.addRow(self.qlabel1, self.i1)
                self.formlayout.addRow(self.qlabel2, self.i2)

            elif self.selected == 'Bluetooth':
                self.devices.clear()
                self.qlabel1 = QtWidgets.QLabel(self.formBox)
                self.qlabel1.setText("Dispositivos: ")
                self.pick_bluetooth = QtWidgets.QComboBox()
                available_devices = bluetooth.discover_devices(duration=5, lookup_names=True)
                for addr, name in available_devices:
                    self.devices[name] = addr
                    self.pick_bluetooth.addItem(name)

                self.formlayout.addRow(self.qlabel1, self.pick_bluetooth)

            else:  # It can only be Internet option
                self.qlabel1 = QtWidgets.QLabel(self.formBox)
                self.qlabel2 = QtWidgets.QLabel(self.formBox)
                self.qlabel1.setText('IP')
                self.qlabel2.setText('Puerto')
                self.transport = QtWidgets.QComboBox()
                self.transport.addItem("TCP")
                self.transport.addItem("UDP")
                self.i1 = QtWidgets.QLineEdit()
                self.i2 = QtWidgets.QLineEdit()

                self.formlayout.addRow(self.qlabel1, self.i1)
                self.formlayout.addRow(self.transport)
                self.formlayout.addRow(self.qlabel2, self.i2)
        except Exception as err:
            print(err)

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

        if self.validate_input(comm_args) and self.widgetCoord.set_comm(comm_args):
            # Enable dc
            self.menu_action.setEnabled(False)
            self.start_action.setEnabled(True)
            self.stop_action.setEnabled(False)
        else:
            ErrorMessageWrapper('Error de conexión', 'Se produjo un error en la configuración de la conexión')
        super().accept()

    @staticmethod
    def validate_input(comm_args):
        if comm_args['type'] == 'Serial':
            for (port, desc, hardware_id) in comports(include_links=False):
                if comm_args['port'] == port:
                    try:
                        baud = int(comm_args['baudrate'])
                        if baud > 0:
                            return True
                        else:
                            return False
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


class PlotForm(QtWidgets.QDialog):
    def __init__(self, widget_coord, pin_dict, debug_vars):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self._color_dict = {'r': 'Rojo',
                            'g': 'Verde',
                            'b': 'Azul',
                            'c': 'Celeste',
                            'm': 'Cian',
                            'y': 'Amarillo',
                            'k': 'Negro',
                            'w': 'Blanco'}

        self.setWindowTitle("Añadir nueva pestaña gráfica")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.widgetCoord = widget_coord
        self.pin_dict = pin_dict
        self.debug_vars = debug_vars
        self._selected_row = 0

        # Some shenanigans to identify later what can be plotted
        pin_dict_cpy = pin_dict.copy()
        for key in debug_vars.keys():
            pin_dict_cpy[key] = [key]
        self.plt_dict = pin_dict_cpy
        # form Box
        formlayout = QtWidgets.QFormLayout()
        formbox = QtWidgets.QGroupBox("Configuración general")
        self.lineedit1 = QtWidgets.QLineEdit()
        self.lineedit1.setStatusTip('Expression to evaluate when upon recieving a pin '
                                    'value, leave blank to plot the just the pin value')
        qlabel1 = QtWidgets.QLabel('Titulo')
        formlayout.addRow(qlabel1, self.lineedit1)

        add_button = QtWidgets.QPushButton("Añadir")
        self.delete_button = QtWidgets.QPushButton("Suprimir")
        self.delete_button.setEnabled(False)

        # Attach functions to buttons
        add_button.clicked.connect(self.on_click_add)
        self.delete_button.clicked.connect(self.delete_row)

        button_container = QtWidgets.QHBoxLayout()
        button_container.addWidget(add_button)
        button_container.addWidget(self.delete_button)

        # A table to display the given data given on the dialog
        # created by the add_button
        self.qt_table = QtWidgets.QTableWidget()
        self.qt_table.setColumnCount(3)
        self.qt_table.setRowCount(0)
        self.qt_table.setHorizontalHeaderLabels(['Pin', 'Expresión', 'Color'])
        self.qt_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.qt_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.qt_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.qt_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.qt_table.itemClicked.connect(self.selected_row)

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
        self.PinEvalDialog(self, self.plt_dict, color_dict=self._color_dict)

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

    def delete_row(self):
        if self.selected_row:
            actual_row = self._selected_row - 1
            self.qt_table.removeRow(actual_row)
            self._selected_row = None
            # no hay columnas deshabilitamos delete
            if not self.qt_table.rowCount():
                self.delete_button.setEnabled(False)

    def selected_row(self, item):
        self.qt_table.selectRow(item.row())
        self._selected_row = item.row() + 1  # Shenanigan

    # TODO: Support for debug vars too
    def accept(self):
        n_rows = self.qt_table.rowCount()
        if n_rows:
            conf_plt_items = []
            for current_row in range(0, n_rows):
                item_pin = self.qt_table.item(current_row, 0)
                item_math = self.qt_table.item(current_row, 1)
                item_color = self.qt_table.item(current_row, 2)

                if item_pin and item_math and item_color:
                    key = item_pin.text()
                    number = self.plt_dict[key]
                    math_expression = item_math.text()
                    color_val = item_color.text()
                    color_key = list(self._color_dict.keys())[list(self._color_dict.values()).index(color_val)]
                    conf_plt_items.append((key, number, math_expression, color_key))

            # Call the core to instantiate the PlotWidget
            general_config = dict()
            general_config['title'] = self.lineedit1.text()
            self.widgetCoord.create_plot_widget(general_config, conf_plt_items)
        super().accept()

    class PinEvalDialog(QtWidgets.QDialog):
        def __init__(self, form_to_notify, plt_dict, color_dict):
            QtWidgets.QDialog.__init__(self)
            self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
            self.setWindowTitle(" ")
            self.setFixedWidth(300)
            self.setFixedHeight(150)
            self.plt_form = form_to_notify

            qlabel1 = QtWidgets.QLabel("Pin:")
            qlabel2 = QtWidgets.QLabel("Expresión a evaluar:")
            qlabel3 = QtWidgets.QLabel("Color:")

            self.pin_selector = QtWidgets.QComboBox()
            for plt_id in sorted(plt_dict.keys()):
                self.pin_selector.addItem(str(plt_id))
            self.to_evaluate = QtWidgets.QLineEdit()
            self.pick_color = QtWidgets.QComboBox()
            for color in sorted(color_dict.values()):
                self.pick_color.addItem(color)

            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            button_box.rejected.connect(self.reject)
            button_box.accepted.connect(self.accept)

            main_layout = QtWidgets.QVBoxLayout()
            form_layout = QtWidgets.QFormLayout()
            form_layout.addRow(qlabel1, self.pin_selector)
            form_layout.addRow(qlabel2, self.to_evaluate)
            form_layout.addRow(qlabel3, self.pick_color)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)

            self.exec_()

        def accept(self):
            # Get the user input and give it to form_to_notify
            pin_selected = self.pin_selector.currentText()
            eval_string = self.to_evaluate.text()
            color_selected = self.pick_color.currentText()
            # Handle adquired data to the PlotForm object
            self.plt_form.add_new_row(pin_selected, eval_string, color_selected)
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
            ErrorMessageWrapper.instance = self
            self.err_title = err_title
            self.err_str = err_str
            self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
            self.setWindowTitle(self.err_title)
            self.showMessage(self.err_str)
            self.exec_()

        def __del__(self):
            ErrorMessageWrapper.instance = None
