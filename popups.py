from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout

class ModbusPopup(Popup):

    _info_lb = None
    def __init__(self, server_ip, server_port, **kwargs):
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_porta.text = str(server_port)
    
    def setInfo(self, message):
        self._info_lb = Label(text = message)
        self.ids.layout.add_widget(self._info_lb)
    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)
class ScanPopup(Popup):
    def __init__(self, scantime, **kwargs):
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)
class SetPointPopup(Popup):
    pass
class DataGraphPopup(Popup):
    def __init__(self, xmax,ymax,y_ticks_major, plot_color,**kwargs):
        super().__init__(**kwargs)
        
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax
        self.ids.graph.ymax = ymax
        self.ids.graph.y_ticks_major = y_ticks_major
class LabeledCheckBoxDataGraph(BoxLayout):
    pass

class HistGraphPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.get('tags').items():
            cb = LabeledCheckBoxHistGraph()
            cb.ids.label.text = key +  value['unidade']

            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)

class LabeledCheckBoxHistGraph(BoxLayout):
    pass
