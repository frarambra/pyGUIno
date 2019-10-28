from utils import CustomWidgets
from utils.Communication import CommunicationWrapper
import logging


class Core:
    def __init__(self, layout, comm_args, list_widgets):
        print("Core: Instanciando")
        self.non_free_spots = []
        self.commands = [
            # 0, no se hace tracking de los valores; 1 se hace tracking al valor, la posicion indica el pin
            # orden: A0->AX, despues los digitales
            ["add_track_pin", "?*"],
            ["stop_track_pin", "i*"],  # First arg will be the number of pins to stop then the pin_id
            ["get_debug_vars", ""],
            ["set_debug_var_value", ""],
            ["await_pins", "i*"]
        ]
        self.comm = None
        # Procedemos a iniciar la comunicacion
        self.layout = layout
        if comm_args:
            pass  # self.comm = Communication.AbstractCommunication(comm_args)
        # Iniciamos los loggers
        self.logs = ['I2C', 'SPI', 'COM']
        # noinspection PyShadowingBuiltins
        for id in self.logs:
            log = logging.getLogger(id)
            log.setLevel(logging.INFO)

        # TODO: Inicializacion de los customsWidgets
        if list_widgets is None:
            self.list_widgets = []

        # Nuestras cosas de informacion
        # loop = asyncio.get_event_loop()
        print("Core: Instanciado")

    # Communication related methods
    def set_comm(self, comm_args):
        self.comm = CommunicationWrapper(comm_args)

    def handle_new_data(self):
        msg = self.comm.recieve()
        command = msg[0]

        if command == self.commands[0]:
            pass
        elif command == self.commands[1]:
            pass
        elif command == self.commands[2]:
            pass
        elif command == self.commands[3]:
            pass
        elif command == self.commands[5]:
            pass
        elif command == self.commands[6]:
            pass

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

    def create_plot_widget(self, pin):
        plt_widget = CustomWidgets.WidgetPlot(pin=pin)
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
