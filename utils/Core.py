from utils import Communication, CustomWidgets
import logging


class Core:
    def __init__(self, layout, comm_args, list_widgets):
        self.non_free_spots = []
        # Procedemos a iniciar la comunicacion
        self.layout = layout
        if comm_args:
            self.comm = Communication.AbstractCommunication(comm_args)
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
