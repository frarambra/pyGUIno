from PyQt5 import QtWidgets, QtCore
from serial.tools.list_ports import comports
from functools import partial
import re


class ConnectionForm(QtWidgets.QDialog):
    def __init__(self, args):
        print("ConnectionForm: Instanciando")
        QtWidgets.QDialog.__init__(self)
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

        elif self.selected == 'Bluetooth':
            pass

        self.formBox.setLayout(formlayout)
        self.mainLayout.addWidget(self.formBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.exec_()

    @QtCore.pyqtSlot()
    def accept(self):
        print('ConnectionForm: aceptado, procedemos a añadir al core la AbstractCommunication')
        comm_args = {'type': self.selected}
        if self.selected == 'Serial':
            comm_args['port'] = self.i1.text()
            comm_args['baudrate'] = self.i2.text()
            print('ConnectionForm: datos serial añadidos')
        elif self.selected == 'WiFi':
            comm_args['ip'] = self.i1.text()
            comm_args['protocol'] = self.transport.currentText()
            comm_args['port'] = self.i2.text()
            print('ConnectionForm: datos wifi añadidos')

        print('ConnectionForm: valores de comm_args\n{}'.format(comm_args))
        if self.validate_input(comm_args):
            self.core.set_comm(comm_args)
            super().accept()

        else:
            error_msg = QtWidgets.QErrorMessage()
            error_msg.showMessage("Error en los argumentos")
            error_msg.exec_()

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

        else:  # TODO change to elif comm_args['type'] == 'Wifi': | Isn't working elif for some reason
            print('Validando los datos')
            valid_ip_address = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
            if re.match(valid_ip_address, comm_args['ip']):
                print('Regex bueno')
                try:
                    port_number = int(comm_args['port'])
                    print('port number {}'.format(port_number))
                    if 0 < port_number <= 65535:
                        return True
                except ValueError:
                    return False
            else:
                return False

        return False


class PlotForm(QtWidgets.QDialog):
    def __init__(self, core, pin_dict):
        QtWidgets.QDialog.__init__(self)
        print("PlotForm: Instantiating")
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
        self.modify_button = QtWidgets.QPushButton("Modify")
        self.delete_button.setEnabled(False)
        self.modify_button.setEnabled(False)

        # Attached functions to buttons

        self.pin_dict = pin_dict
        add_button.clicked.connect(self.on_click_add)

        button_container = QtWidgets.QHBoxLayout()
        button_container.addWidget(add_button)
        button_container.addWidget(self.delete_button)
        button_container.addWidget(self.modify_button)

        # A table to display the given data given on the dialog
        # created by the add_button
        self.qt_table = QtWidgets.QTableWidget()
        self.qt_table.setColumnCount(2)
        self.qt_table.setRowCount(0)
        self.qt_table.setHorizontalHeaderLabels(['Pins', 'Eval'])
        # TODO: Make a proper configuration of the table

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
        print("PlotForm: Created")

    def on_click_add(self):
        # open a PinEvalDialog
        PinEvalDialog(self, pin_dict=self.pin_dict)

    def add_new_row(self, pin_selected, eval_string):
        self.delete_button.setEnabled(True)
        self.modify_button.setEnabled(True)
        append_row = self.qt_table.rowCount()
        self.qt_table.insertRow(append_row)
        tmp1 = QtWidgets.QTableWidgetItem(pin_selected)
        tmp2 = QtWidgets.QTableWidgetItem(eval_string)
        self.qt_table.setItem(append_row, 0, tmp1)
        self.qt_table.setItem(append_row, 1, tmp2)

    def accept(self):
        try:
            n_rows = self.qt_table.rowCount()
            conf_plt_pins = []
            for current_row in range(0, n_rows):
                tmp1 = self.qt_table.item(current_row, 0)
                tmp2 = self.qt_table.item(current_row, 1)
                if tmp1 and tmp2:
                    pin_key = tmp1.text()
                    pin_number = self.pin_dict[pin_key]
                    math_expression = tmp2.text()
                    conf_plt_pins.append((pin_number, math_expression))

            # Call the core to instantiate the PlotWidget
            general_config = dict()
            general_config['title'] = self.lineedit1.text()
            self.coreRef.create_plot_widget(general_config, conf_plt_pins)
        except Exception as err:
            print(err)
        finally:
            super().accept()


class PinEvalDialog(QtWidgets.QDialog):
    def __init__(self, form_to_notify, pin_dict):
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(" ")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        qlabel1 = QtWidgets.QLabel("Pin")
        qlabel2 = QtWidgets.QLabel("Expression to value:")

        self.pin_selector = QtWidgets.QComboBox()

        for pin_id in sorted(pin_dict.keys()):
            self.pin_selector.addItem(str(pin_id))
        self.to_evaluate = QtWidgets.QLineEdit()

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(partial(self.custom_accept, form_to_notify=form_to_notify))

        main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(qlabel1, self.pin_selector)
        form_layout.addRow(qlabel2, self.to_evaluate)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # self.show()
        self.exec_()

    def custom_accept(self, form_to_notify):
        # Get the user input and give it to form_to_notify
        pin_selected = self.pin_selector.currentText()
        eval_string = self.to_evaluate.text()

        # Handle adquired data to the PlotForm object
        form_to_notify.add_new_row(pin_selected, eval_string)
        super().accept()
