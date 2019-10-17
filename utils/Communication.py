import serial


class AbstractCommunication:
    def __init__(self, args):
        comm_type = args['type']
        self.comm_obj = None
        if comm_type == 'serial':
            self.comm_obj = CommSerial(args)
        elif comm_type == 'wifi':
            self.comm_obj = CommWifi(args)
        elif comm_type == 'bluetooth':
            self.comm_obj = CommBluetooth(args)


class CommSerial:
    def __init__(self, args):
        port = args['port']
        baudrate = args['baudrate']
        self.ser = serial.Serial(port=port, baudrate=baudrate)
        self.ser.open()
        print("Comunicacion iniciada")

    def request_from_arduino(self, pin):
        self.ser.write("r:{}\r\n".format(pin))

    def read_from_arduino(self):
        ard_inf = self.ser.readline()
        print(ard_inf)

class CommWifi:
    def __init__(self, *args):
        print("CommWifi creado")


class CommBluetooth:
    def __init__(self, *args):
        print("CommBluetooth creado")
