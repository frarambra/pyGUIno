from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, \
    QPushButton, QTableWidget, QHBoxLayout, QTableWidgetItem, QDialog, QComboBox, QLineEdit, QDialogButtonBox, \
    QFormLayout
from PyQt5.QtCore import pyqtSlot


import pyqtgraph as pg
import time
import logging


# TODO: Avoid the y axis move that much when several pins are being plotted
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
        print(pin_and_eval)

        for tmp in pin_and_eval:
            plt_item = self.plot_widget.getPlotItem()
            plt_aux_tmp = self.PltAux(pin=tmp[0], plt_item=plt_item)
            self.contained_plots.append(plt_aux_tmp)

    def new_data(self, data, timestamp):
        pin = data[0]
        value = data[1]
        for plt_aux in self.contained_plots:
            if plt_aux.pin == str(pin):
                plt_aux.update(timestamp-self.t_ini, value)

    # TODO: Implement evaluation function with either exec or eval
    class PltAux:
        def __init__(self, pin, plt_item):
            # Length must match
            self.limit = 500
            self.pin = pin
            self.plt_item = plt_item
            self.time_axe = []
            self.value_axe = []

        def update(self, ts, value):
            self.shift(ts, value)
            self.plt_item.clear()
            self.plt_item.plot(self.time_axe, self.value_axe)

        def shift(self, ts, value):
            if len(self.time_axe) >= self.limit:
                self.time_axe.pop(0)
                self.value_axe.pop(0)
            self.time_axe.append(ts)
            self.value_axe.append(value)


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
        try:
            msg = record.getMessage()
            splitted_record = msg.split('\\')
            if splitted_record[0] == self.log_id:
                self.loggerText.appendPlainText(splitted_record[1])
        except Exception as err:
            print(err)


class UserVarsTable(QWidget):
    def __init__(self, user_vars):
        QWidget.__init__(self, parent=None)
        self.mainLayout = QHBoxLayout()
        self.ArduinoTable = QTableWidget()  # VarName | Value | Adress | Type?
        self.UserTable = QTableWidget()  # VarName | str(value) or math expression
        self.user_vars = user_vars

        self.ArduinoTable.setColumnCount(4)
        self.ArduinoTable.setRowCount(0)
        self.UserTable.setColumnCount(2)
        self.UserTable.setRowCount(0)

        self.ArduinoTable.setHorizontalHeaderLabels(['Arduino variables', 'Value', 'Address', 'Data Type'])
        self.UserTable.setHorizontalHeaderLabels(['User variables', 'Value'])

        # Set of buttons for UserTable, use some sort of icons, +, crank, -
        button_container = QVBoxLayout()
        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton('Delete')
        self.modify_button = QPushButton('Modify')

        self.add_button.clicked.connect(self.open_add_dialog)
        self.delete_button.clicked.connect(self.delete_from_user_vars)

        button_container.addWidget(self.add_button)
        button_container.addWidget(self.delete_button)
        button_container.addWidget(self.modify_button)

        # Set up layout and add widgets
        self.setLayout(self.mainLayout)
        self.layout().addWidget(self.ArduinoTable)
        self.layout().addWidget(self.UserTable)
        self.layout().addLayout(button_container)

        # Delete
        self.show()

    def new_arduino_data(self, data):
        append_row = self.ArduinoTable.rowCount()

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

    def open_add_dialog(self):
        try:
            self.AddUserVarMenu(self.UserTable, self.user_vars)
        except Exception as err:
            print(err)

# TODO: IMPORTANTE QUIZAS LA FORMA DE SALVAR EL TEMA CUSTOM VARIABLES SEA MEDIANTE FORMAT STRINGS
    def delete_from_user_vars(self, key):
        if key in self.user_vars.keys():
            del self.user_vars[key]

    def modify_user_var(self, key, new_value):
        if key in self.user_vars.keys():
            if self.check_expression(new_value):
                try:
                    int(new_value)
                except ValueError:
                    try:
                        float(new_value)
                    except ValueError:
                        # Show message error
                        pass
                else:
                    self.user_vars[key] = new_value

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
