from utils import communication, CustomWidgets
import logging
import asyncio


class Core:
    def __init__(self, layout, type_comm, comm_args, list_widgets):
        self.non_free_spots = [(0,1),(1,0),(1,1)]
        # Procedemos a iniciar la comunicacion
        self.layout = layout
        if type_comm is not None:
            self.comm = self.set_comm(type_comm, comm_args)
        # Iniciamos los loggers
        self.logs = ['I2C', 'SPI', 'SERIAL']
        # noinspection PyShadowingBuiltins
        for id in self.logs:
            log = logging.getLogger(id)
            log.setLevel(logging.INFO)

        # TODO: Inicializacion de los customsWidgets
        if list_widgets is None:
            self.list_widgets = []

        # Nuestras cosas de informacion
        # loop = asyncio.get_event_loop()

    # Para cuando le den a cargar
    def core_load(self, args):
        # usar los datos de args y llamar al constructor
        pass

    # Esto deberia ser async
    def handle_new_data(self):
        data = self.comm.getData()  # La estructura del mensaje deberia ser [PIN | Valor | timestamp]
        for widget in self.list_widgets:
            widget.new_data(data)

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

    def create_plot_widget(self, pin):
        plt_widget = CustomWidgets.WidgetPlot(pin=pin)
        self.list_widgets.append(plt_widget)
        (cord_x, cord_y) = self.manage_layout()
        self.layout.addWidget(plt_widget, cord_x, cord_y, 1, 1)

    def manage_layout(self):
        if self.non_free_spots is []:
            return 0, 1
        else:
            x = []
            y = []
            for (temp1, temp2) in self.non_free_spots:
                x.append(temp1)
                y.append(temp2)
            if min(x) <= min(y):
                self.non_free_spots.append((min(x)+1, min(y)))
                return min(x)+1, min(y)
            else:
                self.non_free_spots.append((min(x), min(y)+1))
                return min(x), min(y)+1
