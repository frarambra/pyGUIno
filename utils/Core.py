from utils import CustomWidgets
import logging
import PyCmdMessenger
import asyncio


class Core:
    def __init__(self, layout, comm_args):
        print("Core: Instantiating")
        self.non_free_spots = []
        self.list_widgets = []
        self.debug_var = []
        self.commands = [
            ["ack_start", "s"],  # To recieve: With this we will be aware when the communication has started
            ["request_pin", "i"],  # To send: First arg will be the number of pins to start tracking then the pin number
            ["arduino_transmit_pin_value", "ii"],  # To recieve: we recieve the pin and value
            ["request_debug_var_value", "iI"],  # To send: type of data and memory address
            ["answer_debug_var_value", "b*"],  # To recieve: the value as an bunch of bytes
            ["arduino_transmit_debug_var", "iIs"]   # To recieve: type of data, memory address, human identifier
        ]
        self.comm = None
        # Procedemos a iniciar la comunicacion
        self.layout = layout
        if comm_args:
            pass  # self.comm = Communication.AbstractCommunication(comm_args)
        # Iniciamos los loggers

        logs = ['I2C', 'SPI', 'SERIAL']
        # noinspection PyShadowingBuiltins
        for id in logs:
            log = logging.getLogger(id)
            log.setLevel(logging.INFO)

    # Communication related methods
    def set_comm(self, comm_args):
        arduino = PyCmdMessenger.ArduinoBoard(comm_args['port'], comm_args['baudrate'],
                                              timeout=3.0, settle_time=3.0)
        self.comm = PyCmdMessenger.CmdMessenger(arduino, self.commands)

    async def handle_new_data(self):
        log = logging.getLogger('SERIAL')
        while True:
            msg = await self.comm.recieve()
            if msg:
                log.info(msg)
                command = msg[0]
                payload = msg[1]

                if command == self.commands[0]:  # ack_start
                    print("Communication started {}".format(payload))
                elif command == self.commands[2]:  # arduino_transmit_pin_value
                    for widget in self.list_widgets:
                        if isinstance(widget, CustomWidgets.WidgetPlot):
                            widget.new_data(data=payload)
                elif command == self.commands[5]:  # arduino_transmit_debug_var
                    # TODO: Decidir sobre como vamos a tratar este tema
                    # data_type = payload[0]
                    # mem_addr = payload[1]
                    # var_name = payload[2]
                    pass

    def start_recieve_loop(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.handle_new_data())
        loop.run_forever()

    # Widget related methods
    @staticmethod
    def logger_notify(name, data):
        log = logging.getLogger(name)
        log.info(data)

    def create_logger_widget(self, log_id):
        logger_widget = CustomWidgets.CustomLogger(log_id=log_id)
        self.list_widgets.append(logger_widget)
        (cord_x, cord_y) = self.manage_layout()
        self.layout.addWidget(logger_widget, cord_x, cord_y, 1, 1)

    def create_plot_widget(self, plot_args):
        plt_widget = CustomWidgets.WidgetPlot(plot_args)
        self.list_widgets.append(plt_widget)
        (cord_x, cord_y) = self.manage_layout()
        self.layout.addWidget(plt_widget, cord_x, cord_y, 1, 1)

    def manage_layout(self):
        if not self.non_free_spots:
            x = 0
            y = 0
        # si el segundo elemento de la lista es 0
        elif self.non_free_spots[-1][1] == 0:
            x = self.non_free_spots[-1][0]
            y = self.non_free_spots[-1][1]+1
        else:
            x = self.non_free_spots[-1][0]+1
            y = 0  # La y deberia ser 0
        self.non_free_spots.append((x, y))
        return x, y
