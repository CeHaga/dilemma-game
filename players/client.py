from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
import rpyc

import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"
class ClientService(rpyc.Service):
    def __init__(self, app):
        self.app = app

    def exposed_receive_message(self, message):
        # This method is exposed to be called by the server
        self.app.handle_server_message(message)

class ClientApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect_to_server()
        self.player_name = ""

    def connect_to_server(self):
        client_service = ClientService(self)
        self.conn = rpyc.connect("localhost", 12345, service=client_service, config={'allow_all_attrs': True, 'allow_public_attibutes': True})

    def handle_server_message(self, message):
        print(f'Server message: {message}')
        # You can add more logic here to update the UI based on the message

    def build(self):
        sm = ScreenManager()
        sm.add_widget(NameScreen(name="name"))
        sm.add_widget(WaitGameStart(name="wait_game_start"))
        return sm

    def on_stop(self):
        self.conn.close()

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
        if app.conn.root.login(app.player_name, app.conn):
            app.root.current = "wait_game_start"

class WaitGameStart(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text="Esperando jogo começar..."))
        self.add_widget(layout)

if __name__ == "__main__":
    ClientApp().run()
