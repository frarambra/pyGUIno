from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, \
    QPushButton, QTableWidget, QHBoxLayout, QTableWidgetItem
from PyQt5.QtCore import pyqtSlot


import pyqtgraph as pg
import time
import logging


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
        for plt_aux in self.contained_plots:
            if plt_aux.pin == str(pin):
                plt_aux.update(timestamp-self.t_ini, value)

    # TODO: Implement evaluation function with either exec or eval
    class PltAux:
        def __init__(self, pin, plt_item):
            # Length must match
            self.limit = 1000
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
    def __init__(self):
        QWidget.__init__(self, parent=None)
        self.mainLayout = QHBoxLayout()
        self.ArduinoTable = QTableWidget()  # VarName | Value | Adress | Type?
        self.UserTable = QTableWidget()  # VarName | str(value) or math expression

        self.ArduinoTable.setColumnCount(4)
        self.UserTable.setColumnCount(2)
        self.ArduinoTable.setHorizontalHeaderLabels(['Arduino variables', 'Value', 'Address', 'Data Type'])
        self.UserTable.setHorizontalHeaderLabels(['User variables', 'Value'])

        # Set of buttons for UserTable, use some sort of icons, +, crank, -
        button_container = QVBoxLayout()
        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton('Delete')
        self.modify_button = QPushButton('Modify')
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
                value_item.setText(data['value'])
                return
        self.ArduinoTable.insertRow(append_row)
        var_name_item = QTableWidgetItem(data['name'])
        value_item = QTableWidgetItem(data['value'])
        addr_item = QTableWidgetItem(data['addr'])
        data_type_item = QTableWidgetItem(data['data_type'])
        self.ArduinoTable.setItem(append_row, 0, var_name_item)
        self.ArduinoTable.setItem(append_row, 1, value_item)
        self.ArduinoTable.setItem(append_row, 2, addr_item)
        self.ArduinoTable.setItem(append_row, 3, data_type_item)
