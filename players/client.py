import sys
sys.path.append('../')

import rpyc
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from game_enums import *

# Define the callback function that will handle messages from the server
def callback(message):
    print(f"Received callback with message: {message}")

# Function to continuously listen for callbacks from the server
def listen_for_callbacks(conn):
    try:
        while True:
            conn.serve(0.1)  # Serve requests with a timeout of 0.1 seconds
    except Exception as e:
        print(f"Error while listening for callbacks: {e}")

class ClientApp(App):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.username = ""
        self.is_waiting_start = False
        self.players = []
        self.callbacks = {
            'start_game': self.start_game,
        }

    def build(self):
        sm = ScreenManager()
        sm.add_widget(NameScreen(name="name"))
        sm.add_widget(WaitGameStartScreen(name="wait_game_start"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(WaitPlayersSelectScreen(name="wait_players_select"))
        return sm
    
    def start_game(self, players):
        self.players = [p['username'] for p in players]
        Clock.schedule_once(self._change_to_game_screen)

    def next_round(self, player_scores):
        print(f"Scores: {player_scores}")
        self.root.current = 'game'

    def _change_to_game_screen(self, dt):
        if self.root.current == 'wait_game_start':
            self.root.current = 'game'

    def on_stop(self):
        self.conn.close()

    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        self._username = value
        self.conn.username = value
        print(self.conn.username)

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
        username = self.name_input.text

        # Check if the player name is valid
        if len(username) == 0:
            popup = Popup(title="Please enter a name", size_hint=(None, None), size=(200, 100))
            popup.open()
            return
        
        # Check only alphanumeric characters are used
        if not username.isalnum():
            popup = Popup(title="Please enter only alphanumeric characters", size_hint=(None, None), size=(200, 100))
            popup.open()
            return
        
        if len(username) > 10:
            popup = Popup(title="Please enter a name shorter than 10 characters", size_hint=(None, None), size=(200, 100))
            popup.open()
            return

        login_result = app.conn.root.login(username, app.conn, app.callbacks)

        print(f"Login result: {login_result}")

        if login_result == LoginResult.SUCCESS:
            app.username = username
            app.root.current = "wait_game_start"
        else:
            popup_title = ""
            
            if login_result == LoginResult.GAME_STARTED:
                popup_title = "Game already started"
            elif login_result == LoginResult.USERNAME_IN_USE:
                popup_title = "Username already in use"
                
            popup = Popup(title=popup_title, size_hint=(None, None), size=(200, 200))
            popup.open()

class WaitGameStartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.add_widget(Label(text="Waiting for game to start..."))
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        app.is_waiting_start = True

class GameScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        app.is_waiting_start = False

        main_layout = BoxLayout(orientation="vertical")
        betray_layout = GridLayout(cols=3)
        for player in app.players:
            if player == app.username:
                continue
            button = Button(text=player)
            button.bind(on_press=self.on_select)
            betray_layout.add_widget(button)
        main_layout.add_widget(betray_layout)

        main_layout.add_widget(Button(text="Cooperate"))
        self.add_widget(main_layout)

    def on_select(self, instance):
        app = App.get_running_app()
        app.conn.root.betray(app.username, instance.text)
        app.root.current = "wait_players_select"

class WaitPlayersSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.add_widget(Label(text="Waiting for players to select..."))
        self.add_widget(layout)


if __name__ == "__main__":
    # Establish connection to the server
    conn = rpyc.connect("localhost", 12345, config={"allow_all_attrs": True})

    # Start a thread to handle incoming callbacks
    callback_thread = threading.Thread(target=listen_for_callbacks, args=(conn,))
    callback_thread.daemon = True  # The thread will close when the main program exits
    callback_thread.start()

    # Start the Kivy app
    ClientApp(conn).run()
