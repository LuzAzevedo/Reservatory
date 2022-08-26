from kivy.uix.boxlayout import BoxLayout
from popups import HistGraphPopup, ModbusPopup, ScanPopup, DataGraphPopup, SetPointPopup
from kivy.core.window import Window
from kivy.uix.image import Image
from threading import Thread
from time import sleep
from datetime import datetime
from db_handler import DBHandler
from kivy_garden.graph import LinePlot
from modbus_client import ClientModbus
from controller import Controller
import random
import timeseriesgraph

class MainWidget(BoxLayout): #Widget principal

    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20


    def __init__(self, **kwargs):
        super().__init__()
        
        self._scan_time = kwargs.get('scan_time')
        #modbus
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP,self._serverPort)
        
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = ClientModbus(self._serverIP, self._serverPort)
        self._setPointPopup = SetPointPopup()
        
        self._meas ={}
        self._meas['timestamp'] = None
        self._meas['values'] ={}

        self._tags['motor_freq']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':10,'unidade': ' [Hz]'}
        self._tags['voltage']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':1,'unidade': ' [V]'}
        self._tags['rotation']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':1,'unidade': ' 100*[rpm]'}
        self._tags['input_power']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':10,'unidade': ' 100*[W]',}
        self._tags['current']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':100,'unidade': ' [A]'}
        self._tags['temp_stator']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':10,'unidade': ' [ºC]'}
        self._tags['input_flow']= {'color':(random.random(),random.random() ,random.random() ,1),'multiplicador':100,'unidade': ' [m³/s]'}
        self._tags['level']= {'color':(0,0 ,1 ,1),'multiplicador':10,'unidade': ' 10*[L]'}

        self._graphLevel = DataGraphPopup(self._max_points,1000,100,self._tags['level']['color'])
        self._graphInput = DataGraphPopup(self._max_points, 10 ,1,self._tags['input_flow']['color'])
        self._hgraph = HistGraphPopup(tags = self._tags)
        self._db = DBHandler(kwargs.get('db_path'),self._tags)

        self._controller = Controller(
            lambda x: self._modbusClient.set_data("motor_state", x),
            lambda: self._modbusClient.get_data("motor_state"),
            lambda: self._modbusClient.get_data("level"),
            lambda x: self._modbusClient.set_data("desired_freq", x),
            lambda: self._modbusClient.get_data("temp_stator"),
            self._scan_time/1000
        )
        self._controller.set_target(0)
        
        
    

    def startDataRead(self, ip, port):
        #Método para configurar ip e porta do Servidor MODBUS e
        
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open_client()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open():
                self._modbusClient.set_data("start_time", 2)
                self._updateThread = Thread(target=self.updater, daemon=True)
                self._updateThread.start()
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Erro no startDataRead", e.args)
    
    
    def updater(self):
        
        while self._updateWidgets:
            try:
                if not self._modbusClient.is_open():
                    self.ids.img_con.source = 'imgs/desconectado.png'
                    continue
                    
                self._controller.control_step()
                self.readData()
                self.updateGUI()
                self._db.insert_data(self._meas )
            except Exception as e :
                print("Erro no updater: ", e.args)
            sleep(self._scan_time/1000)

    def readData(self):
        """
        Metodo para leitura dos dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()  #retorna o horário corrente do sistema operacional
        for key ,value in self._modbusClient.inputs.items():
            self._meas['values'][key] = self._modbusClient.get_data(key)
        
    def updateGUI(self):

        self._img_max = None
        self._img_low = None
        #Atualiza interface grafica a partir dos dados lidos
        self._graphLevel.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['level']),0)
        self._graphInput.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['input_flow']),0)
        #Atualização do nivel da temperatura do motor
        self.ids.lb_temp.size = (165*self._modbusClient.get_data("temp_stator")/60, self.ids.lb_temp.size[1])
        #Atualização do nivel do volume do reservatório
        self.ids.lb_vol.size = (self.ids.lb_vol.size[0], 15.1*self._modbusClient.get_data("level")/100)
        #Atualização dos dados da tabela
        self.ids.motor_freq.text = ('[color=2961a6]' + str(self._modbusClient.get_data("motor_freq")) + '[/color]' + '[color=2961a6] Hz[/color]')
        self.ids.voltage.text = ('[color=2961a6]' + str(self._modbusClient.get_data("voltage")) + '[/color]' + '[color=2961a6] V[/color]')
        self.ids.rotation.text = ('[color=2961a6]' + str(self._modbusClient.get_data("rotation")) + '[/color]' + '[color=2961a6] rpm[/color]')
        self.ids.input_power.text = ('[color=2961a6]' + str(self._modbusClient.get_data("input_power")) + '[/color]' + '[color=2961a6] W[/color]')
        self.ids.current.text = ('[color=2961a6]' + str(self._modbusClient.get_data("current")) + '[/color]' + '[color=2961a6] A[/color]')
        self.ids.temp_stator.text = ('[color=2961a6]' + str(self._modbusClient.get_data("temp_stator")) + '[/color]' + '[color=2961a6] ºC[/color]')
        self.ids.input_flow.text = ('[color=2961a6]' + str(self._modbusClient.get_data("input_flow")) + '[/color]' + '[color=2961a6] m³/s[/color]')
        self.ids.level.text = ('[color=2961a6]' + str(self._modbusClient.get_data("level")) + '[/color]' + '[color=2961a6] L[/color]')
        #Atualização do SetPoint
        self.ids.sp_img.pos_hint = {'x': 0.27, 'y': 0.575+(0.275*self._controller.target/1000)}
        #Atualização estado da bomba
        if self._modbusClient.get_data("motor_state"):
            self.ids.motor.text = '[color=2961a6]ON[/color]'
            self.ids.motor1.size_hint = (0.17, 0.17)
            self.ids.motor0.size_hint = (0.17, 0.0)
        else:
            self.ids.motor.text = '[color=2961a6]OFF[/color]'
            self.ids.motor0.size_hint = (0.17, 0.17)
            self.ids.motor1.size_hint = (0.17, 0.0)
        
        for i in range (1, 4):
            if self._modbusClient.get_data(f"valve_{i}"):
                self.ids[f"valve_{i}"].text = '[color=2961a6]HIGH[/color]'
            else:
                self.ids[f"valve_{i}"].text = '[color=2961a6]LOW[/color]'
        
        if self._modbusClient.get_data("level_high"):
            self.ids.al1_img.size_hint = (0.055,0.055)
        
        elif not self._modbusClient.get_data("level_low"):
            self.ids.al2_img.size_hint = (0.055,0.055)
        
        elif not self._modbusClient.get_data("level_high") and self._modbusClient.get_data("level_low"):
            self.ids.al1_img.size_hint = (0.055,0.0)
            self.ids.al2_img.size_hint = (0.055,0.0)

    def stopRefresh(self):
        self._updateWidgets = False

    def getDataDB(self):
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)
            if init_t is None or final_t is None or len(cols)==0:
                return
            
            cols.append('timestamp')

            dados = self._db.select_data(cols, init_t, final_t)

            if dados is None or len(dados['timestamp'])==0:
                return
            
            self._hgraph.ids.graph.clearPlots()
            for key, value in dados.items():
                if key == 'timestamp':
                    continue
                if key == 'level':
                    p = LinePlot(line_width = 1.5, color = self._tags[key]['color'])
                    p.points = [(x, value[x]/10) for x in range(0, len(value))]
                elif key== 'rotation' or key =='input_power':
                    p = LinePlot(line_width = 1.5, color = self._tags[key]['color'])
                    p.points = [(x, value[x]/100) for x in range(0, len(value))]
                else:
                    p = LinePlot(line_width = 1.5, color = self._tags[key]['color'])
                    p.points = [(x, value[x]) for x in range(0, len(value))]
                self._hgraph.ids.graph.add_plot(p)
            self._hgraph.ids.graph.xmax = len(dados[cols[0]])
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in dados['timestamp']])
        except Exception as e:
            print("Erro no getDataDB: ", e.args)
            

    def parseDTString (self, datetime_str):
        #converte a string inserida para o formato utilizado na busca no BD
        try:
            d = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro: ", e.args)

    def onOffSwitch(self, button, button_id):
        if button.text == '[color=2961a6]LOW[/color]':
            button.text = '[color=2961a6]HIGH[/color]'
            self._modbusClient.set_data(button_id, 1)
        else:
            button.text = '[color=2961a6]LOW[/color]'
            self._modbusClient.set_data(button_id, 0)
