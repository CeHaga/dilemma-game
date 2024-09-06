import sys

sys.path.append("../")

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
from kivy.logger import Logger
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
        Logger.exception(e)


class ClientApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._username = None
        self.ip = None
        self.is_waiting_start = False
        self.players = []
        self.callbacks = {
            "start_game": self.start_game,
            "is_alive": self.is_alive,
            "next_turn": self.next_turn,
        }

    def build(self):
        sm = ScreenManager()
        sm.add_widget(NameScreen(name="name"))
        sm.add_widget(WaitGameStartScreen(name="wait_game_start"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(WaitPlayersSelectScreen(name="wait_players_select"))
        sm.add_widget(ScoreScreen(name="score"))
        sm.add_widget(ReconnectionScreen(name="reconnection"))
        sm.add_widget(EndScreen(name="end"))
        return sm

    def start_game(self, players):
        self.players = [p["username"] for p in players]
        Clock.schedule_once(self._change_to_game_screen)

    def is_alive(self):
        return True

    def next_turn(self, player_scores, last_round):
        print(f"Scores: {player_scores}")
        self.scores = player_scores
        if last_round:
            Clock.schedule_once(self._change_to_end_screen)
        else:
            Clock.schedule_once(self._change_to_score_screen)

    def _change_to_game_screen(self, dt):
        if self.root.current == "wait_game_start":
            self.root.current = "game"

    def _change_to_next_turn(self, dt):
        if self.root.current == "wait_players_select":
            self.root.current = "game"

    def _change_to_score_screen(self, dt):
        if self.root.current == "wait_players_select":
            self.root.current = "score"

    def _change_to_end_screen(self, dt):
        if self.root.current == "wait_players_select":
            self.root.current = "end"

    def on_stop(self):
        try:
            self.conn.close()
        except:
            pass

    def check_connection(self, dt):
        try:
            self.conn.ping()
        except:
            self.last_screen = self.root.current
            self.root.current = "reconnection"
            Clock.unschedule(self.check_connection)
            Clock.schedule_once(self.attempt_reconnect, 1)

    def attempt_reconnect(self, dt):
        try:
            print(f"Connecting to IP {self.ip}")
            self.conn = rpyc.connect(self.ip, 12345)
        except Exception as e:
            Logger.exception(e)
            self.root.current = "name"
            return

        self.conn.username = self.username
        self.conn.callbacks = self.callbacks

        scores = self.conn.root.relogin(self.username, self.conn, self.callbacks)

        Clock.schedule_interval(self.check_connection, 1)
        self.scores = scores
        self.root.current = self.last_screen

    def login(self, username, ip):
        try:
            self.conn = rpyc.connect(ip, 12345, config={"allow_all_attrs": True})
        except Exception as e:
            Logger.exception(e)
            return LoginResult.WRONG_IP
        self.ip = ip

        # Start a thread to handle incoming callbacks
        callback_thread = threading.Thread(
            target=listen_for_callbacks, args=(self.conn,)
        )
        callback_thread.daemon = True
        callback_thread.start()

        result = self.conn.root.login(username, self.conn, self.callbacks)
        if result != LoginResult.SUCCESS:
            return result
        self.username = username
        Clock.schedule_interval(self.check_connection, 1)
        return LoginResult.SUCCESS

    def disconnect(self, instance):
        try:
            self.conn.close()
            self.conn = None
        except:
            pass

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.conn.username = value

    def disconnect_button(self):
        button = Button(text="Disconnect")
        button.bind(on_press=self.disconnect)
        return button


class NameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")

        app = App.get_running_app()

        self.name_input = TextInput(multiline=False, hint_text="Enter your name")

        self.ip_input = TextInput(multiline=False, hint_text="Enter server IP")

        submit_button = Button(text="Submit")
        submit_button.bind(on_press=self.submit_name)

        layout.add_widget(self.name_input)
        layout.add_widget(self.ip_input)
        layout.add_widget(submit_button)
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        if app.username:
            self.name_input.text = app.username
        if app.ip:
            self.ip_input.text = app.ip

    def submit_name(self, instance):
        app = App.get_running_app()
        username = self.name_input.text

        # Check if the player name is valid
        if len(username) == 0:
            popup = Popup(
                title="Please enter a name", size_hint=(None, None), size=(200, 100)
            )
            popup.open()
            return

        # Check only alphanumeric characters are used
        if not username.isalnum():
            popup = Popup(
                title="Please enter only alphanumeric characters",
                size_hint=(None, None),
                size=(200, 100),
            )
            popup.open()
            return

        if len(username) > 10:
            popup = Popup(
                title="Please enter a name shorter than 10 characters",
                size_hint=(None, None),
                size=(200, 100),
            )
            popup.open()
            return

        login_result = app.login(username, self.ip_input.text)

        if login_result == LoginResult.SUCCESS:
            app.username = username
            app.root.current = "wait_game_start"
            return

        popup_title = ""

        if login_result == LoginResult.GAME_STARTED:
            popup_title = "Game already started"
        elif login_result == LoginResult.USERNAME_IN_USE:
            popup_title = "Username already in use"
        elif login_result == LoginResult.WRONG_IP:
            popup_title = "Wrong IP"

        popup = Popup(title=popup_title, size_hint=(None, None), size=(200, 200))
        popup.open()


class WaitGameStartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.add_widget(Label(text="Waiting for game to start..."))
        app = App.get_running_app()
        self.add_widget(app.disconnect_button())
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

        cooperate_button = Button(text="Cooperate")
        cooperate_button.bind(on_press=self.on_cooperate)
        main_layout.add_widget(cooperate_button)

        main_layout.add_widget(app.disconnect_button())
        self.add_widget(main_layout)

    def on_select(self, instance):
        app = App.get_running_app()
        app.conn.root.betray(app.username, instance.text)
        app.root.current = "wait_players_select"

    def on_cooperate(self, instance):
        app = App.get_running_app()
        app.conn.root.betray(app.username, None)
        app.root.current = "wait_players_select"


class WaitPlayersSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.add_widget(Label(text="Waiting for players to select..."))
        app = App.get_running_app()
        self.add_widget(app.disconnect_button())
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        app.is_waiting_start = False
        app.is_waiting_select = True


class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.score_label = Label(text="")
        layout.add_widget(self.score_label)

        continue_button = Button(text="Continue")
        continue_button.bind(on_press=self.on_continue)
        layout.add_widget(continue_button)

        app = App.get_running_app()
        layout.add_widget(app.disconnect_button())

        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        app.is_waiting_start = False
        app.is_waiting_select = False
        app.is_game_over = False

        self.score_label.text = f"Scores:\n"
        print(app.scores)
        for player, score in app.scores["scores"].items():
            self.score_label.text += f"{player}: {score}\n"

    def on_continue(self, instance):
        app = App.get_running_app()
        app.root.current = "game"


class EndScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.score_label = Label(text="")
        layout.add_widget(self.score_label)
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        app.is_waiting_start = False
        app.is_waiting_select = False
        app.is_game_over = True

        self.score_label.text = f"Scores:\n"
        for player, score in app.scores["scores"].items():
            self.score_label.text += f"{player}: {score}\n"


class ReconnectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.add_widget(Label(text="Reconnecting..."))
        self.add_widget(layout)


if __name__ == "__main__":
    # Start the Kivy app
    ClientApp().run()
