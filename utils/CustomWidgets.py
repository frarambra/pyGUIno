from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, \
    QPushButton, QTableWidget, QHBoxLayout, QTableWidgetItem, QDialog, QComboBox, QLineEdit, QDialogButtonBox, \
    QFormLayout, QAbstractItemView, QHeaderView
from PyQt5 import QtCore

import pyqtgraph as pg
import time
import logging


# TODO: Avoid the y axis move that much when several pins are being plotted
class WidgetPlot(QWidget):
    def __init__(self, configuration_data, config_plt_data, user_dict_ref):
        QWidget.__init__(self)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setLayout(QVBoxLayout())
        self.plot_widget = pg.PlotWidget(background='w')
        self.layout().addWidget(self.plot_widget)

        self.contained_plots = []
        self.resources = dict()
        # Set title and such from "meta"

        for tmp in config_plt_data:
            plt_item = self.plot_widget.getPlotItem()
            plt_aux_tmp = self.PltAux(pin_key=tmp[0], pin_number=tmp[1],
                                      math_expression=tmp[2], color= tmp[3],
                                      plt_item=plt_item)
            self.resources[tmp[0]] = tmp[1]
            self.contained_plots.append(plt_aux_tmp)

        self.user_dict_ref = user_dict_ref

    def new_data(self, data, timestamp):
        pin = data[0]
        value = data[1]

        for plt_aux in self.contained_plots:
            if plt_aux.pin == pin:
                # Get pin_id by pin_number
                pin_key = list(self.resources.keys())[list(self.resources.values()).index(pin)]
                tmp_dict = self.user_dict_ref.copy()
                tmp_dict[pin_key] = value
                plt_aux.update(timestamp, value, tmp_dict)

    class PltAux:
        def __init__(self, pin_key, pin_number, math_expression, color, plt_item):
            # Length must match
            self.limit = 500
            self.t_ini = time.time()
            self.pin_key = pin_key
            self.pin = pin_number
            self.plt_item = plt_item
            self.math_expression = math_expression
            self.color = color
            self.time_axe = []
            self.value_axe = []

        def update(self, ts, value, dict_user_ref):
            if len(self.time_axe) >= self.limit:
                self.time_axe.pop(0)
                self.value_axe.pop(0)
            # Eval and add to the axis
            try:
                if self.math_expression != "":
                    value = eval(self.math_expression.format_map(dict_user_ref))
            except SystemError as err:
                print('Error on eval, showing raw data')
                print(err)
            finally:
                self.time_axe.append(ts-self.t_ini)
                self.value_axe.append(value)
                self.plt_item.clear()
                self.plt_item.plot(self.time_axe, self.value_axe,
                                   pen=self.color)


class CustomLogger(QWidget, logging.Handler):
    def __init__(self, log_id):
        QWidget.__init__(self)
        self.log_id = log_id

        logging.Handler.__init__(self)
        self.log = logging.getLogger(log_id)
        self.log.addHandler(self)

        base = QVBoxLayout()
        self.setLayout(base)

        self.loggerText = QPlainTextEdit()
        self.loggerText.setReadOnly(True)

        self.title = QLabel()
        self.title.setText(log_id+" Logger")

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.loggerText)

    def emit(self, record):
        msg = record.getMessage()
        self.loggerText.appendPlainText(msg)


class DebugVarsTable(QWidget):
    def __init__(self, debug_vars):
        QWidget.__init__(self, parent=None)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet('background-color:white')
        self.ArduinoTable = QTableWidget()  # VarName | Value | Adress | Type
        self._selected_row = None
        self.debug_vars = debug_vars

        self.ArduinoTable.setColumnCount(4)
        self.ArduinoTable.setRowCount(0)

        # Configure the table settings
        self.ArduinoTable.setHorizontalHeaderLabels(['Arduino variables', 'Value', 'Address', 'Data Type'])
        self.ArduinoTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ArduinoTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ArduinoTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ArduinoTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ArduinoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set up layout and add widgets
        self.setLayout(self.mainLayout)
        self.layout().addWidget(self.ArduinoTable)

    def new_arduino_data(self, data):
        append_row = self.ArduinoTable.rowCount()
        # Update table
        for row in range(0, append_row):
            item_tmp = self.ArduinoTable.item(row, 0)
            if item_tmp.text() == data['name']:
                value_item = self.ArduinoTable.item(row, 1)
                value_item.setText(str(data['value']))
                return
        self.ArduinoTable.insertRow(append_row)
        var_name_item = QTableWidgetItem(str(data['name']))
        value_item = QTableWidgetItem(str(data['value']))
        addr_item = QTableWidgetItem(hex(data['addr']))
        data_type_item = QTableWidgetItem(str(data['data_type']))
        self.ArduinoTable.setItem(append_row, 0, var_name_item)
        self.ArduinoTable.setItem(append_row, 1, value_item)
        self.ArduinoTable.setItem(append_row, 2, addr_item)
        self.ArduinoTable.setItem(append_row, 3, data_type_item)

        # Update user_dict
        self.debug_vars[data['name']] = data['value']


class UserVarsTable(QWidget):
    def __init__(self, user_vars):
        QWidget.__init__(self, parent=None)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet('background-color:white')
        self.UserTable = QTableWidget()  # VarName | str(value) or math expression
        self._selected_row = None
        self.user_vars = user_vars

        self.UserTable.setColumnCount(2)
        self.UserTable.setRowCount(0)

        # Configure the table settings
        self.UserTable.setHorizontalHeaderLabels(['User variables', 'Value'])
        self.UserTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.UserTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.UserTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Add event handlers
        self.UserTable.itemClicked.connect(self.selected_row)

        # Set of buttons for UserTable, use some sort of icons, +, crank, -
        button_container = QVBoxLayout()
        button_container.setContentsMargins(0, 0, 0, 0)
        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton('Delete')

        self.add_button.clicked.connect(self.open_add_dialog)
        self.delete_button.clicked.connect(self.delete_from_user_vars)

        button_container.addWidget(self.add_button)
        button_container.addWidget(self.delete_button)

        # Set up layout and add widgets
        self.setLayout(self.mainLayout)
        self.layout().addWidget(self.UserTable)
        self.layout().addLayout(button_container)

    def open_add_dialog(self):
        try:
            self.AddUserVarMenu(self.UserTable, self.user_vars)
        except Exception as err:
            print(err)

    def delete_from_user_vars(self):
        if self._selected_row and bool(self.user_vars):
            actual_row = self._selected_row - 1
            key = self.UserTable.item(actual_row, 0).text()
            self.UserTable.removeRow(actual_row)
            del self.user_vars[key]
            self._selected_row = None

    def selected_row(self, item):
        self.UserTable.selectRow(item.row())
        self._selected_row = item.row() + 1  # Shenanigan
        print('Selected row: {}'.format(self._selected_row))

    class AddUserVarMenu(QDialog):
        def __init__(self, user_table, user_dict):
            QDialog.__init__(self)
            self.user_table = user_table
            self.user_dict = user_dict

            self.setWindowTitle(" ")
            self.setFixedWidth(300)
            self.setFixedHeight(150)

            qlabel1 = QLabel("Variable name:")
            qlabel2 = QLabel("Variable value:")

            self.var_name = QLineEdit()
            self.var_value = QLineEdit()

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.rejected.connect(self.reject)
            button_box.accepted.connect(self.add_to_user_vars)

            main_layout = QVBoxLayout()
            form_layout = QFormLayout()
            form_layout.addRow(qlabel1, self.var_name)
            form_layout.addRow(qlabel2, self.var_value)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)

            self.show()
            self.exec_()

        def add_to_user_vars(self):
            key = self.var_name.text()
            value = self.var_value.text()

            if key not in self.user_dict.keys():
                # Check if it's an integer then a float
                try:
                    float(value)
                except ValueError as err:
                    # This aint a number, show error message
                    print(err)
                else:
                    # Add to dictionary and update table
                    self.user_dict[key] = value
                    append_row = self.user_table.rowCount()
                    self.user_table.insertRow(append_row)
                    item_name = QTableWidgetItem(key)
                    item_value = QTableWidgetItem(value)
                    self.user_table.setItem(append_row, 0, item_name)
                    self.user_table.setItem(append_row, 1, item_value)
                finally:
                    print(self.user_dict)
                    super().accept()
