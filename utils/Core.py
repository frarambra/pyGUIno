from utils import communication
import logging, asyncio


class Core:
    def __init__(self, type_comm, comm_args, list_widgets):
        # Procedemos a iniciar la comunicacion
        self.comm = self.set_comm(type_comm, comm_args)
        # Iniciamos los loggers
        self.logs = ['I2C', 'SPI', 'SERIAL']
        # noinspection PyShadowingBuiltins
        for id in self.logs:
            log = logging.getLogger(id)
            log.setLevel(logging.INFO)

        # Inicializacion de los customsWidgets
        self.list_widgets = list_widgets

        # Nuestras cosas de informacion
        # loop = asyncio.get_event_loop()

    # Esto deberia ser async
    def handle_new_data(self):
        data = self.comm.getData()  # La estructura del mensaje deberia ser [PIN | Valor | timestamp]
        for widget in self.list_widgets:
            widget.new_data(data)

    def add_cwidget(self, qwidget):
        self.list_widgets.append(qwidget)

    @staticmethod
    def set_comm(comm, args):
        if comm == 'serial':
            return communication.CommSerial(args)
        elif comm == 'wifi':
            return communication.CommWifi(args)
        else:
            return communication.CommBluetooth(args)

    @staticmethod
    def logger_notify(name, data):
        log = logging.getLogger(name)
        log.info(data)
