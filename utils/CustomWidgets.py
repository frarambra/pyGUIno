from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPlainTextEdit, QPushButton
from PyQt5.QtCore import pyqtSlot

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
import time
import logging


class WidgetPlot(QWidget):
    def __init__(self, pin):
        QWidget.__init__(self)
        # TODO: Cambiar esto es filler y temporal, deberia haber multiples instancias para un mismo pin?
        # haria falta un formulario para escoger la posicion en el grid o bastaria con un "drag and drop"
        self.pin = pin

        base = QVBoxLayout()
        self.setLayout(base)
        # Las canvas de matplotplib
        fig = Figure(figsize=(10, 8))
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.dynamic_canvas = FigureCanvas(fig)
        self.navtoolbar = NavigationToolbar(self.dynamic_canvas, self)

        # Añadimos al layout los ojbetos
        self.nombreGrafica = QLabel()
        self.layout().addWidget(self.nombreGrafica)
        self.layout().addWidget(self.navtoolbar)
        self.layout().addWidget(self.dynamic_canvas)

        # Estilos
        self.nombreGrafica.setText('Grafica '+pin)
        self.nombreGrafica.setMargin(15)

        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._update_canvas()
        self._timer = self.dynamic_canvas.new_timer(10, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        # timestamp = args['timestamp']
        # pin = args['pin']
        # value = args['value']

        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Aqui se deberian obtener los datos del arduino
        self._dynamic_ax.plot(t, 10*np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()
        # self._timer.stop()

    def new_data(self, data):
        # Estructura de datos PIN | dato | timestamp
        ts = data['timestamp']
        pin = data['pin']
        value = data['value']

        if ts or pin or value is None:
            return
        else:
            # TODO: actualizar aquellos plots que requieran los datos
            pass


'''
    Las siguiente clase tiene como objetivo crear un logger funcional con el 
    objetivo de poder mostrar informacion de cualquier tipo, ya sea lo que pase por el serial
    o algun protocolo especifico
'''


class CustomLogger(QWidget, logging.Handler):
    def __init__(self, log_id):
        QWidget.__init__(self)
        self.needed_resources = []

        logging.Handler.__init__(self)
        self.log = logging.getLogger(log_id)
        self.log.addHandler(self)

        base = QVBoxLayout()
        self.setLayout(base)

        # Configuramos donde ira el texto del logger
        self.loggerText = QPlainTextEdit()
        self.loggerText.setReadOnly(True)
        self.loggerText.setFixedHeight(300)
        self.loggerText.setFixedWidth(300)

        # Miscelanea
        self.title = QLabel()
        self.title.setText(log_id+" Logger")
        self.button = QPushButton()
        self.button.clicked.connect(self.click_event)
        self.button.setText('Cerrar')

        # Añadimos todas las cosas para que quede bonito
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.loggerText)

    def emit(self, record):
        msg = 'Contenido del mensaje:\n{}'.format(self.format(record))
        print(msg)
        self.loggerText.appendPlainText(msg)

    # TODO: Borrar esto, solo es temporal
    @pyqtSlot()
    def click_event(self):
        print('click_event ejecutado')
        text = 'Prueba a las {}'.format(time.time())
        self.log.info(text)
