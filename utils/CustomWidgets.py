from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, \
    QPushButton, QTableWidget, QHBoxLayout, QTableWidgetItem, QDialog, QComboBox, QLineEdit, QDialogButtonBox, \
    QFormLayout, QAbstractItemView, QHeaderView

from PyQt5 import QtCore
from utils.Forms import ErrorMessageWrapper
import pyqtgraph as pg
import time
import logging


# https://stackoverflow.com/questions/40577104/how-to-plot-two-real-time-data-in-one-single-plot-in-pyqtgraph

class WidgetPlot(QWidget):
    def __init__(self, configuration_data, config_plt_data,
                 resource_dict_ref, user_dict_ref):
        QWidget.__init__(self)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setLayout(QVBoxLayout())
        plot_widget = pg.PlotWidget(background='w')
        self.layout().addWidget(plot_widget)
        self.pltItem = plot_widget.getPlotItem()

        self.contained_plots = []
        self.resource_dict_ref = resource_dict_ref
        self.user_dict_ref = user_dict_ref
        # Set title and such from "meta"
        self.configuration_data = configuration_data

        for tmp in config_plt_data:
            plt_aux_tmp = self.PltAux(update_variable=tmp[0], math_expression=tmp[1], color=tmp[2],
                                      plt_item=self.pltItem.plot())
            self.contained_plots.append(plt_aux_tmp)

    def new_data(self, data, timestamp):
        update_variable = data[0]
        value = data[1]

        for plt_aux in self.contained_plots:
            if plt_aux.update_variable == update_variable:
                tmp = self.resource_dict_ref.copy()
                tmp.update(self.user_dict_ref)
                # To avoid merging the dicts
                plt_aux.update(timestamp, value, tmp)

    def serialize(self):
        tmp = list()
        for plt_aux in self.contained_plots:
            tmp.append(plt_aux.serialize())
        return_dict = dict()
        return_dict['title'] = self.configuration_data['title']
        return_dict['pltAux_list'] = tmp

        return return_dict

    class PltAux:
        def __init__(self, update_variable, math_expression, color, plt_item):
            # Length must match
            self.limit = 500
            self.first_update = True
            self.t_ini = 0
            self.update_variable = update_variable
            self.curve = plt_item
            self.math_expression = math_expression
            self.color = color
            self.time_axe = []
            self.value_axe = []

        def update(self, ts, value, total_dict):
            if self.first_update:
                self.t_ini = time.time()
                self.first_update = False

            if len(self.time_axe) >= self.limit:
                self.time_axe.pop(0)
                self.value_axe.pop(0)
            # Eval and add to the axis
            try:
                if self.math_expression != "":
                    value = eval(self.math_expression.format_map(total_dict))
            except Exception as err:
                print('Error on eval, showing raw data')
                print(err)
                ErrorMessageWrapper(err.__class__, err)
            finally:
                self.time_axe.append(ts-self.t_ini)
                self.value_axe.append(value)
                self.curve.setData(self.time_axe, self.value_axe, pen=self.color)

        def serialize(self):
            save_dict = dict()
            save_dict['update_variable'] = self.update_variable
            save_dict['color'] = self.color
            if self.math_expression:
                save_dict['math_expression'] = self.math_expression
            else:
                save_dict['math_expression'] = ''

            return save_dict


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
        self.title.setText('Logger')

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.loggerText)

    def emit(self, record):
        msg = record.getMessage()
        self.loggerText.appendPlainText(msg)


class DebugVarsTable(QWidget):
    def __init__(self, resource_dict):
        QWidget.__init__(self, parent=None)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet('background-color:white')
        self.ArduinoTable = QTableWidget()  # VarName | Value | Adress | Type
        self._selected_row = None
        self.resource_dict = resource_dict

        self.ArduinoTable.setColumnCount(4)
        self.ArduinoTable.setRowCount(0)

        # Configure the table settings
        self.ArduinoTable.setHorizontalHeaderLabels(['Identificador', 'Valor',
                                                     'Dirección', 'Tipo de dato'])
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
        self.resource_dict[data['name']] = data['value']


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
        self.UserTable.setHorizontalHeaderLabels(['Parámetro', 'Valor'])
        self.UserTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.UserTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.UserTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Add event handlers
        self.UserTable.itemClicked.connect(self.selected_row)

        # Set of buttons for UserTable, use some sort of icons, +, crank, -
        button_container = QVBoxLayout()
        button_container.setContentsMargins(0, 0, 0, 0)
        self.add_button = QPushButton('Añadir')
        self.delete_button = QPushButton('Suprimir')

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
            self.AddUserVarMenu(user_table=self)
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

    def add_to_user_vars(self, key, value):
        if key not in self.user_vars.keys():
            # Check if it's an integer then a float
            try:
                float(value)
            except ValueError as err:
                # This aint a number, show error message
                ErrorMessageWrapper(err, 'No es un número')
            else:
                # Add to dictionary and update table
                self.user_vars[key] = value
                append_row = self.UserTable.rowCount()
                self.UserTable.insertRow(append_row)
                item_name = QTableWidgetItem(key)
                item_value = QTableWidgetItem(value)
                self.UserTable.setItem(append_row, 0, item_name)
                self.UserTable.setItem(append_row, 1, item_value)

    class AddUserVarMenu(QDialog):
        def __init__(self, user_table):
            QDialog.__init__(self)
            if not user_table:
                print('None de referencia')
            self.user_table = user_table
            self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
            self.setWindowTitle("Añadir parámetro")
            self.setFixedWidth(300)
            self.setFixedHeight(100)

            qlabel1 = QLabel("Nombre del parámetro:")
            qlabel2 = QLabel("Valor del parámetro:")

            self.var_name = QLineEdit()
            self.var_value = QLineEdit()

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.rejected.connect(self.reject)
            button_box.accepted.connect(self.accept)

            main_layout = QVBoxLayout()
            form_layout = QFormLayout()
            form_layout.addRow(qlabel1, self.var_name)
            form_layout.addRow(qlabel2, self.var_value)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)

            self.show()
            self.exec_()

        def accept(self):
            key = self.var_name.text()
            value = self.var_value.text()
            if key and value and key != '' and value != '':
                self.user_table.add_to_user_vars(key, value)
            super().accept()
