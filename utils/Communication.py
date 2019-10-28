import PyCmdMessenger


class CommunicationWrapper:
    def __init__(self, args):
        self.board = None
        self.commands = [
            ["request_pin", "i"],  # First arg will be the number of pins to start tracking then the pin number
            ["transmit_pin_value", "ii"],  # First arg will be the number of pins to stop tracking then the pin numer
            ["transmit_debug_var", "iis"]  # type of data, memory address, human identifier
        ]

        if args['type'] == 'Serial':
            self.board = PyCmdMessenger.ArduinoBoard(args['port'], args['baudrate'])
            self.cmd = PyCmdMessenger.CmdMessenger(self.board, self.commands)
        elif args['type'] == 'WiFi':
            self.board = PlaceHolder()
        elif args['type'] == 'Bluetooth':
            self.board = PlaceHolder()

    def recieve(self):
        # This function is blocking thus it should be on the loop
        msg = self.cmd.receive()
        return msg


class PlaceHolder:
    def __init__(self):
        pass

    def recieve(self):
        pass

    def send(self, args):
        pass
