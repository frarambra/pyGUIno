from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton
from PyQt5.QtCore import pyqtSlot, QTimer

import pyqtgraph as pg
import numpy as np
import time
import logging


class WidgetPlot(QWidget):
    def __init__(self, pin_and_eval):
        QWidget.__init__(self)
        # haria falta un formulario para escoger la posicion en el grid o bastaria con un "drag and drop"
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setLayout(QVBoxLayout())
        self.plot_widget = pg.PlotWidget(background='w')
        self.layout().addWidget(self.plot_widget)
        self.val1 = self.plot_widget.getPlotItem()
        self.val2 = self.plot_widget.getPlotItem()
        self.val1.plot()
        self.val2.plot(pen='b')

        self.label = QLabel()
        self.layout().addWidget(self.label)

        # Set Data

        self.x = np.linspace(0, 50., num=100)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        # Start
        self._update()

    def _update(self):

        self.data = 2*np.cos(self.x/3.+self.counter/9.)
        self.ydata = np.sin(self.x/3.+self.counter/9.)
        self.val1.clear()
        self.val2.clear()
        self.val1.plot(self.data, pen=pg.mkPen(color=(255, 0, 0)))
        self.val2.plot(self.ydata, pen=pg.mkPen(color=(0, 0, 255)))

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QTimer.singleShot(1, self._update)
        self.counter += 1

    def new_data(self, data):
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
