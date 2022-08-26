from typing import Callable

class Controller:
    # Coloquei uma frequência mínima negativa para criar um certo buffer
    # Quando o nível é um pouco acima do alvo, o ruído de leitura fica ligando
    # e desligando o motor. Colocando um mínimo fora da zona de atuação deixa
    # uma área para 'absorver' esse ruído. O mínimo enviado de verdade é 0
    min_freq = -20
    max_freq = 60
    max_level = 9000
    max_temp = 130
    thresh_temp = 80
    temp_factor = 0.2
    PI = (1.2, 0.3)

    def __init__(self, set_motor_state: Callable, 
                  get_motor_state: Callable,
                  get_level: Callable,
                  set_desired_freq: Callable,
                  get_motor_temp: Callable,
                  delta_time: float) -> None:
        
        self.send_motor_state = set_motor_state
        self.get_motor_state = get_motor_state
        self.get_level = get_level
        self.send_desired_freq = set_desired_freq
        self.get_motor_temp = get_motor_temp

        self.delta_time = delta_time

        self.set_motor_state(0)
        self._desired_freq = self.min_freq
        self.send_desired_freq(self.max_freq)

        self.control = True
        self.target = 0
        self.last_level = self.get_level() or 0

    def set_target(self, value: float):
        self.target = value
        self.control = True

    def set_motor_state(self, value: bool):
        self.send_motor_state(value)
    
    def set_desired_freq(self, value: float):
        if value > self.max_freq:
            value = self.max_freq

        if value <= 0:
            self.set_motor_state(0)
            if value < self.min_freq:
                value = self.min_freq
        else:
            if not self.get_motor_state():
                self.set_motor_state(1) 

        self._desired_freq = value
        self.send_desired_freq(value if value > 0 else 0)

    def control_step(self):
        
        if not self.control:
            return

        level = self.get_level()
        if level == None:       # None se não abriu o server
            return
        
        error = self.target - level

        flow = (level - self.last_level) / self.delta_time
        self.last_level = level
        temp = self.get_motor_temp()

        if level > self.max_level or temp > self.max_temp:
            self.set_desired_freq(0)
            self.set_motor_state(0)
            return
        
        control = error * self.PI[1] - flow * self.PI[0]
        
        if temp > self.thresh_temp:
            control -= (temp - self.thresh_temp) * self.temp_factor

        self.set_desired_freq(self._desired_freq + control*self.delta_time)        
