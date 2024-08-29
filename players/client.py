from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
import rpyc


class NameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.name_input = TextInput(multiline=False)
        submit_button = Button(text="Submit")
        submit_button.bind(on_press=self.submit_name)
        layout.add_widget(Label(text="Enter your name:"))
        layout.add_widget(self.name_input)
        layout.add_widget(submit_button)
        self.add_widget(layout)

    def submit_name(self, instance):
        app = App.get_running_app()
        app.player_name = self.name_input.text
        if app.conn.root.add_connection(app.player_name, app.conn):
            app.root.current = "wait_game_start"

class WaitGameStart(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text="Esperando jogo começar..."))
        self.add_widget(layout)

class ClientApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = rpyc.connect("localhost", 12345)  # Adjust host and port as needed
        self.player_name = ""

    def build(self):
        sm = ScreenManager()
        sm.add_widget(NameScreen(name="name"))
        sm.add_widget(WaitGameStart(name="wait_game_start"))
        return sm

    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    ClientApp().run()
