import PyCmdMessenger


class AbstractCommunication:
    def __init__(self, args):
        commands = [
            # 0, no se hace tracking de los valores; 1 se hace tracking al valor, la posicion indica el pin
            # orden: A0->AX, despues los digitales
            ["add_track_pin", "?*"],
            ["stop_track_pin", "i*"],  # First arg will be the number of pins to stop then the pin_id
            ["get_var_dirs", ""],
            ["get_var_value", ""],
            ["set_var_value", ""],
            ["await_pins", "i*"]
        ]
        print("Communication: Instanciando comunicacion: "+args['type'])
        comm_type = args['type']
        self.comm_obj = None
        if comm_type == 'Serial':
            self.comm_obj = CommSerial(args)
        elif comm_type == 'WiFi':
            self.comm_obj = CommWifi(args)
        elif comm_type == 'Bluetooth':
            self.comm_obj = CommBluetooth(args)


class CommSerial:
    def __init__(self, args):
        pass

    def request_from_arduino(self, pin):
        pass

    def read_from_arduino(self):
        pass


class CommWifi:
    def __init__(self, *args):
        print("CommWifi creado")


class CommBluetooth:
    def __init__(self, *args):
        print("CommBluetooth creado")
