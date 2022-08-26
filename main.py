from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

class MainApp(App):
    def build(self):
        self._widget = MainWidget(scan_time=1000, server_ip = 'localhost', server_port = 502,
        db_path = "db\\scada.db"
        )
        return self._widget

def on_stop(self):
    """
    Método exectutado quando a aplicação é fehcada
    """
    self._widget.stopRefresh()
    

if __name__ == "__main__":
    Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    Builder.load_string(open("popups.kv", encoding="utf-8").read(), rulesonly=True)
    MainApp().run()