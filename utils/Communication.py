import bluetooth


class ArduinoBoardBluetooth:
    def __init__(self, mac_addr,
                 timeout=3.0,
                 int_bytes=2,
                 long_bytes=4,
                 float_bytes=4,
                 double_bytes=4):

        self.mac_addr = mac_addr
        self.timeout = timeout

        self.int_bytes = int_bytes
        self.long_bytes = long_bytes
        self.float_bytes = float_bytes
        self.double_bytes = double_bytes

        # Create bluetooth socket to start connection
        self.bluetooth_socket = None
        self._is_connected = False
        self.open()

        # Limits for the board, rest of the __init__ is code from
        # Michael J. Harms code for PyCmdMessenger
        self.int_min = -2 ** (8 * self.int_bytes - 1)
        self.int_max = 2 ** (8 * self.int_bytes - 1) - 1

        self.unsigned_int_min = 0
        self.unsigned_int_max = 2 ** (8 * self.int_bytes) - 1

        self.long_min = -2 ** (8 * self.long_bytes - 1)
        self.long_max = 2 ** (8 * self.long_bytes - 1) - 1

        self.unsigned_long_min = 0
        self.unsigned_long_max = 2 ** (8 * self.long_bytes) - 1

        # Set to either IEEE 754 binary32 bit or binary64 bit
        if self.float_bytes == 4:
            self.float_min = -3.4028235E+38
            self.float_max = 3.4028235E+38
        elif self.float_bytes == 8:
            self.float_min = -1e308
            self.float_max = 1e308
        else:
            err = "float bytes should be 4 (32 bit) or 8 (64 bit)"
            raise ValueError(err)

        if self.double_bytes == 4:
            self.double_min = -3.4028235E+38
            self.double_max = 3.4028235E+38
        elif self.double_bytes == 8:
            self.double_min = -1e308
            self.double_max = 1e308
        else:
            err = "double bytes should be 4 (32 bit) or 8 (64 bit)"
            raise ValueError(err)

        # ----------------------------------------------------------------------
        # Create a self.XXX_type for each type based on its byte number. This
        # type can then be passed into struct.pack and struct.unpack calls to
        # properly format the bytes strings.
        # ----------------------------------------------------------------------

        INTEGER_TYPE = {2: "<h", 4: "<i", 8: "<l"}
        UNSIGNED_INTEGER_TYPE = {2: "<H", 4: "<I", 8: "<L"}
        FLOAT_TYPE = {4: "<f", 8: "<d"}

        try:
            self.int_type = INTEGER_TYPE[self.int_bytes]
            self.unsigned_int_type = UNSIGNED_INTEGER_TYPE[self.int_bytes]
        except KeyError:
            keys = list(INTEGER_TYPE.keys())
            keys.sort()

            err = "integer bytes must be one of {}".format(keys())
            raise ValueError(err)

        try:
            self.long_type = INTEGER_TYPE[self.long_bytes]
            self.unsigned_long_type = UNSIGNED_INTEGER_TYPE[self.long_bytes]
        except KeyError:
            keys = list(INTEGER_TYPE.keys())
            keys.sort()

            err = "long bytes must be one of {}".format(keys())
            raise ValueError(err)

        try:
            self.float_type = FLOAT_TYPE[self.float_bytes]
            self.double_type = FLOAT_TYPE[self.double_bytes]
        except KeyError:
            keys = list(self.FLOAT_TYPE.keys())
            keys.sort()

            err = "float and double bytes must be one of {}".format(keys())
            raise ValueError(err)
        pass

    def open(self):
        port = 1
        try:
            self.bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.bluetooth_socket.settimeout(self.timeout)
            self.bluetooth_socket.connect((self.mac_addr, port))
        except bluetooth.btcommon.BluetoothError as err:
            # Error handler
            print(err)
        else:
            self._is_connected = True

    def read(self):
        # Must return a byte as ArduinoBoard does
        return self.bluetooth_socket.recv(1)

    def readline(self):
        # Must return a whole line
        # This method is never used by CmdMessenger class though
        try:
            raw_msg = self.bluetooth_socket.recv(1024)
            decoded_msg = raw_msg.decode('utf-8')[:-1]
        except UnicodeDecodeError as err:
            print(err)
            return None
        else:
            return decoded_msg

    def write(self, msg):
        self.bluetooth_socket.send(msg)

    def close(self):
        if self._is_connected:
            self.bluetooth_socket.close()
        self._is_connected = False

    @property
    def connected(self):
        return self._is_connected
