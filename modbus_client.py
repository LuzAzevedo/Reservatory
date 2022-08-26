from pyModbusTCP.client import ModbusClient
from threading import Lock

class ClientModbus:

    coils = {
        "motor_state": 800,
        "valve_1": 801,
        "valve_2": 802,
        "valve_3": 803
    }

    discrete_inputs = {
        "level_high": 809,
        "level_low": 810
    }

    # (multiplicador, endereco)
    holdings = {
        "desired_freq": (1, 799),
        "start_time": (10, 798)
    }

    # (multiplicador, endereco)
    inputs = {
        "motor_freq": (10, 800),
        "voltage": (1, 801),
        "rotation": (1, 803),
        "input_power": (10, 804),
        "current": (100, 805),
        "temp_stator": (10, 806),
        "input_flow": (100, 807),
        "level": (10, 808),
    }

    def __init__(self, server_ip: str, port: int):
        self._client = ModbusClient(host=server_ip, port=port)
        self._lock = Lock

    def change_config(self, server_ip: str, port: int):
        if self._client.is_open:
            self._client.close()

        self._client.host = server_ip
        self._client.port = port
    
    def open_client(self) -> bool:
        return self._client.open()

    def get_data(self, tag: str):
        if not self._client.is_open:
            print("Could not read - client closed")
            return None
        
        if tag in self.coils.keys():
            return self._client.read_coils(self.coils[tag])[0]
        
        if tag in self.holdings.keys():
            return self._client.read_holding_registers(self.holdings[tag][1])[0] \
                        / self.holdings[tag][0]
        
        if tag in self.inputs.keys():
            return self._client.read_input_registers(self.inputs[tag][1])[0] \
                        / self.inputs[tag][0]
        
        if tag in self.discrete_inputs.keys():
            return self._client.read_discrete_inputs(self.discrete_inputs[tag])[0]
        
        print("Could not read - tag was not found")
        return None

    def set_data(self, tag: str, value) -> bool:
        if not self._client.is_open:
            print("Could not write - client closed")
            return False
        
        if tag in self.coils.keys():
            return self._client.write_single_coil(self.coils[tag], value)
        
        if tag in self.holdings.keys():
            return self._client.write_single_register(self.holdings[tag][1],
                                                              int(value * self.holdings[tag][0]))
        
        print("Could not write - tag was not found or was read only")
        return False

    def is_open(self):
        return self._client.is_open
