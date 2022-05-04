import time
import bluetooth
import logging
from datetime import datetime

class SamsungMXT40:
    """
    Bluetooth communication with Samsung MX-T40 Sound Tower

    :param device: The device MAC Address.
    :type device: str
    :var SEQUENCE_NUMBER: the sequence number which gets increase after each send
    :vartype SEQUENCE_NUMBER: int
    :var TYPE_DATA: const 1
    :vartype TYPE_DATA: int
    :var source_map: mapping of return value from device to source name
    :vartype source_map: mapping: dict(int, str)
    :var source_switch_rev_map: mapping of source name to value to send to device
    :vartype source_switch_rev_map: mapping: dict(str, int)
    :var status_map: mapping of light status name to value to send to device
    :vartype status_map: mapping: dict(str, int)
    :var effect_map: mapping of music effect name to value to send to device
    :vartype effect_map: mapping: dict(str, int)
    :var socket: bluetooth socket used to communicate with the device
    :vartype socket: socket
    :var protocol_version: protocol'version returned by the device
    :vartype protocol_version: int
    :var model_info: model returned by the device
    :vartype model_info: int
    :var country_info: country returned by the device
    :vartype country_info: int
    :var num_of_source: Number of sources returned by the device
    :vartype num_of_source: int
    :var group_mode: Group mode returned by the device
    :vartype group_mode: int
    :var source_label: Source Label returned by the device
    :vartype source_label: str
    """

    SEQUENCE_NUMBER = 0
    TYPE_DATA = 1

    source_map = {1: "BT", 2: "USB1", 3: "USB2", 4: "AUX1", 5: "AUX2", 6: "OFF"}
    source_switch_rev_map = {"BT": 1, "USB1": 2, "AUX1": 4, "AUX2": 5}
    status_map = {"OFF": 0, "AMBIENT": 1, "PARTY": 2, "DANCE": 3, "THUNDER": 4, "STAR": 5, "LOVER": 6, "SOLID": 7}
    effect_map = {"OFF": 1, "DELAY": 2, "FILTER": 3, "FLANGER": 4, "CHORUS": 5, "WAHWAH": 6}

    device = None
    socket = None

    protocol_version = -1
    model_info = -1
    country_info = -1
    num_of_source = -1
    group_mode = -1

    source_info = []
    source_label = None
    source_updated_at = None

    def __init__(self, device):
        """
        Init bluetooth connection

        :param device: The device MAC Address.
        :type device: str
        """
        self.device = device
        self.connect()

    def connect(self):
        """
        Open bluetooth connection
        """
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.device, 1))
        except bluetooth.btcommon.BluetoothError:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.device, 2))
        logging.debug("connect_req")
        for command in self.request(self.connect_req()):
            payload = SamsungMXT40.getPayloadData(command)
            self.parse_connect_info(payload)
        logging.debug("connect_link_complete")
        for command in self.request(self.connect_link_complete()):
            payload = SamsungMXT40.getPayloadData(command)

    def close(self):
        """
        Close bluetooth connection
        """
        self.socket.close()
        self.socket = None
        self.SEQUENCE_NUMBER = 0

    def rshift(val, n):
        """
        Rshift Shift of val with n bytes

        :param val: value to shift on the right
        :type val: int
        :param n: number of bytes to shift on the right
        :type n: int
        :return: the actual result of the rshift
        :rtype: int
        """
        return val>>n if val >= 0 else (val+0x100000000) >> n

    def print2HexString(b, b2):
        """
        Convert 2 bytes representing a hex value to string

        :param b: first byte to convert
        :type b: int
        :param b2: second byte to convert
        :type b2: int
        :return: the actual string representation of the hex value
        :rtype: str
        """
        s = hex(b & 255)[2:]
        if (len(s) == 1):
            s = "0" + s
        s3 = hex(b2 & 255)[2:]
        if (len(s3) == 1):
            s = "0" + s
        return s.upper() + s3.upper()

    def printHexString(array):
        """
        Convert an array of bytes to string

        :param array: array of bytes to convert
        :type array: array of bytes
        :return: the actual string rpresentation of the array hex
        :rtype: str
        """
        array2 = []
        for a in array:
            s = hex(a & 255)[2:]
            if (len(s) == 1):
                s = "0" + s
            array2.append(s.upper())
        return array2

    def getCheckSum(n, n2, n3, n4, array):
        """
        Calculate checksum for an array

        :param n: TYPE_DATA
        :type n: int
        :param n2: SEQUENCE_NUMBER
        :type n2: int
        :param n3: length of the array shifted
        :type n3: int
        :param n4: length of the array shifted
        :type n4: int
        :param array: array of data to calculate checksum on
        :type array: array of bytes
        :return: checksum of the array
        :rtype: int
        """
        printHexStr = SamsungMXT40.printHexString(array)
        n5 = 0
        for s in printHexStr:
            n5 += int(s, 16)
        res = (n + n2 + n3 + n4 + n5)
        if res > 128:
            return res-256
        else:
            return res

    def byteToInt(b, b2):
        """
        Convert 2 bytes to int

        :param b: first byte to convert
        :type b: int
        :param b2: second byte to convert
        :type b2: int
        :return: the actual int representation of the bytes
        :rtype: int
        """
        return (SamsungMXT40.rshift(((b & 255) << 24), 16) | (b2 & 255))

    def getDataCommand(self, array):
        """
        Transform an array of bytes in bytes ready to be send to the device

        :param array: array of data to send to the device
        :type array: array of bytes
        :return: bytes to send to the device
        :rtype: bytes
        """
        self.SEQUENCE_NUMBER += 1
        length = len(array)
        n = length + 7
        n2 = SamsungMXT40.rshift((length << 16), 24)
        n3 = SamsungMXT40.rshift((length << 24), 24)
        array2 = []
        array2.append(0)
        array2.append(-69)
        array2.append(self.TYPE_DATA)
        array2.append(self.SEQUENCE_NUMBER)
        array2.append(n2)
        array2.append(n3)
        for b in array:
            if b > 128:
                array2.append(b-256)
            else:
                array2.append(b)
        array2.append(SamsungMXT40.getCheckSum(self.TYPE_DATA, self.SEQUENCE_NUMBER, n2, n3, array))
        logging.debug("DataCommand %s", array2)
        array3 = []
        for c in array2:
            if c > 128:
                array3.append(c-256)
            elif c < 0:
                array3.append(c+256)
            else:
                array3.append(c)
        return bytes(array3)

    def getPayloadData(array):
        """
        Extract payload from array of bytes received from the device

        :param array: array of data received from the device
        :type array: array of bytes
        :return: array of data corresponding to the payload
        :rtype: array of bytes
        """
        if array is None:
            return None
        if array[2] == 0:
            return None
        b = SamsungMXT40.byteToInt(array[4], array[5])
        if b < 1:
            return None
        payload = array[6:].copy()
        logging.debug("PayloadData %s", payload)
        return payload

    def splitCommand(array):
        """
        The device can send various commands in one shot. That's let
        us split them

        :param array: array of data received from the device
        :type array: array of bytes
        :return: array of data corresponding to one command
        :rtype: array of bytes
        """
        commands = []
        if array is None:
            return []
        if len(array) < 7:
            commands.append(array)
            return commands
        start = 0
        while start < len(array):
            cmd_len = SamsungMXT40.byteToInt(array[start + 4], array[start + 5]) + 7
            command = array[start:start+cmd_len]
            logging.debug("Command %s", command)
            commands.append(command)
            start += cmd_len
        return commands

    def request(self, array):
        """
        Send a command to the device and return all the responses separated

        :param array: bytes to send to the device
        :type array: array of bytes
        :return: array of data corresponding to one command
        :rtype: array of bytes
        """
        self.writeBluetooth(array)
        time.sleep(0.1)
        response = self.readBluetooth()
        return SamsungMXT40.splitCommand(response)

    def parse_connect_info(self, array):
        """
        Parse connect info received from the device

        :param array: array of data received from the device
        :type array: array of bytes
        """
        if (array is None or array[0] != 2):
            return None
        self.protocol_version = SamsungMXT40.print2HexString(array[1], array[2])
        self.model_info = array[3]
        self.country_info = array[4]
        self.num_of_source = array[5]
        self.group_mode = array[len(array) - 1]
        self.source_info = ["OFF"]
        for source in array[6:6 + self.num_of_source]:
            self.source_info.append(self.source_map[source])

    def parse_source_info(self, array):
        """
        Parse source info received from the device

        :param array: array of data received from the device
        :type array: array of bytes
        """
        if (array is None or array[0] != 49):
            return None
        self.source_label = self.source_map[array[1]]
        self.source_updated_at = datetime.now()
        logging.info("Source %s", self.source_label)

    def connect_req(self):
        """
        Generate bytes to do a connection request

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([1])

    def connect_restart_req(self):
        """
        Generate bytes to do a connection restart request

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([3])

    def connect_link_complete(self):
        """
        Generate bytes to do a connection link complete request

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([4])

    def source_info_req(self):
        """
        Generate bytes to do a source info request

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([50])

    def usb_control_event(self, b):
        """
        Generate bytes to do a usb control event

        :param b: byte to select the event
        :type b: byte
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([33, b])

    def usb_playtime_enable(self, n):
        """
        Generate bytes to enable usb playtime

        :param n: byte to select the timeframe
        :type n: byte
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([43, n])

    def usb_repeat_mode_setting(self, b):
        """
        Generate bytes to enable usb repeat mode

        :param b: byte to select the mode
        :type b: byte
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([45, 1, b])

    def usb_status_info_req(self):
        """
        Generate bytes to do a usb status info req

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([36])

    def aux_state_req(self):
        """
        Generate bytes to do a aux status info req

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([52])

    def sound_setting(self, b, b2, b3, n):
        """
        Generate bytes to do a sound setting

        :param b: first byte
        :type b: int
        :param b2: second byte
        :type b2: int
        :param b3: third byte
        :type b3: int
        :param n: n byte
        :type n: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        if (b == 5):
            n = 0
        return self.getDataCommand([64, b, b2, b3, n])

    def sound_setting_info_req(self, b):
        """
        Generate bytes to do a sound setting info req

        :param b: first byte
        :type b: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([66, b])

    def system_setting_info_req(self, b):
        """
        Generate bytes to do a system setting info req

        :param b: first byte
        :type b: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([82, b])

    def illumination_setting(self, r, g, b):
        """
        Generate bytes to change the color

        :param r: red color
        :type r: int
        :param g: green color
        :type g: int
        :param b: blue color
        :type b: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([96, 2, r, g, b])

    def status_setting(self, status):
        """
        Generate bytes to change the light status

        :param status: light status name
        :type status: str
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([80, 3, self.status_map[status]])

    def bass_booster_on(self):
        """
        Generate bytes to turn on the bass booster

        :param status: light status name
        :type status: str
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.sound_setting(4, 0, 0, 0)

    def bass_booster_off(self):
        """
        Generate bytes to turn off the bass booster

        :param status: light status name
        :type status: str
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.sound_setting(4, 0, 1, 0)

    def tempo(self, b):
        """
        Generate bytes to change the tempo

        :param b: tempo value
        :type b: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.sound_setting(6, 0, b, 0)

    def change_dj_effect(self, effect, value):
        """
        Generate bytes to change the dj effect

        :param status: effect name
        :type status: str
        :param value: value of the effect to apply
        :type value: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        effect_type = self.effect_map[effect]
        if effect_type == 1:
            value = 0
        logging.debug("change_dj_effect %s %s", effect_type, value)
        return self.getDataCommand([64, 5, 1, effect_type, value])

    def remote_control(self, command):
        """
        Generate bytes to remote control

        :param command: command to send
        :type command: int
        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.getDataCommand([112, command])

    def toggle_on_off(self):
        """
        Generate bytes to toggle on or off the device

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.remote_control(1)

    def sound_more(self):
        """
        Generate bytes to turn up the sound of the device

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.remote_control(15)

    def sound_less(self):
        """
        Generate bytes to turn low the sound of the device

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.remote_control(16)

    def toggle_mute(self):
        """
        Generate bytes to toggle mute on the device

        :return: bytes to send to the device
        :rtype: bytes
        """
        return self.remote_control(20)

    def source_switch(self, source):
        """
        Generate bytes to change the source

        :param status: source name
        :type status: str
        :return: bytes to send to the device
        :rtype: bytes
        """
        self.source_label = source
        self.source_updated_at = datetime.now()
        return self.getDataCommand([48, self.source_switch_rev_map[source]])

    def readBluetooth(self):
        """
        Read socket bluetooth and send it back

        :return: bytes to receive from the device
        :rtype: bytes
        """
        try:
            response = self.socket.recv(1024)
        except bluetooth.btcommon.BluetoothError:
            return None
        if response is None:
            return None
        array = list(response)
        logging.debug("Read %s", array)
        return array

    def writeBluetooth(self, request):
        """
        Write request on the socket bluetooth

        :param request: bytes to send to the device
        :type request: array of bytes
        """
        self.socket.send(request)

    def load_source_info(self):
        """
        Reload source info
        """
        logging.debug("source_info_req")
        for command in self.request(self.source_info_req()):
            payload = SamsungMXT40.getPayloadData(command)
            self.parse_source_info(payload)
        logging.debug("usb_playtime_enable 0")
        for commands in self.request(self.usb_playtime_enable(0)):
            payload = SamsungMXT40.getPayloadData(command)

    def effect_fragment_mode(self):
        """
        Switch to effect fragment mode
        """
        logging.info("sound_setting_info")
        for command in self.request(self.sound_setting_info_req(6)):
            payload = SamsungMXT40.getPayloadData(command)
        logging.info("system_setting_info")
        for command in self.request(self.system_setting_info_req(3)):
            payload = SamsungMXT40.getPayloadData(command)
        logging.info("sound_setting_info")
        for command in self.request(self.sound_setting_info_req(5)):
            payload = SamsungMXT40.getPayloadData(command)
        
    def remote_control_mode(self):
        """
        Switch to remote control mode
        """
        logging.info("sound_setting_info")
        for command in self.request(self.sound_setting_info_req(7)):
            payload = SamsungMXT40.getPayloadData(command)
        logging.info("usb_status_info_req")
        for command in self.request(self.usb_status_info_req()):
            payload = SamsungMXT40.getPayloadData(command)

