from utils import communication, CustomWidgets
import logging

class Core:
    def __init__(self, layout, type_comm, comm_args, list_widgets):
        self.non_free_spots = []
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
        if self.non_free_spots==[]:
            x = 0
            y = 0
        # si el segundo elemento de la lista es 0
        elif self.non_free_spots[-1][1]==0:
            x = self.non_free_spots[-1][0]  # La x deberia mantenerse
            y = self.non_free_spots[-1][1]+1  # La y deberia ser 1
        else:
            x = self.non_free_spots[-1][0]+1  # x deberia aumentarse
            y = 0 # La y deberia ser 0
        self.non_free_spots.append((x, y))
        return x, y