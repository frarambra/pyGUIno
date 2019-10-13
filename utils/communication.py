import time, asyncio, random
import serial


class BaseComm:

    # TODO: Ver que tipos de datos vamos a recuperar de la placa
    def translate_tx(self, bin_input):
        pass

    def translate_rx(self, human_input):
        pass


class CommSerial(BaseComm):
    def __init__(self, args):
        port = args['port']
        baudrate = args['baudrate']
        self.ser = serial.Serial(port=port, baudrate=baudrate)

        # Aqui comienza lo de asyncio

    def start_read(self):
        return self.ser.read()


class CommWifi:
    def __init__(self, *args):
        print("CommWifi creado")


class CommBluetooth:
    def __init__(self, *args):
        print("CommBluetooth creado")
