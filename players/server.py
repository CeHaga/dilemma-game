import sys

sys.path.append("../")

import rpyc
from rpyc.utils.server import ThreadedServer
import threading
from game_enums import *


class MyService(rpyc.Service):
    def __init__(self):
        self.clients = []
        self.game_started = False
        self.player_actions = {}
        self.total_rounds = 1
        self.current_round = 1
        self.total_players = 0
        self.lock = threading.Lock()
        self.player_scores = {}

    def on_disconnect(self, conn):
        print("Client disconnected")
        with self.lock:
            new_clients = []
            for client in self.clients:
                try:
                    client["callbacks"]["is_alive"]()
                    new_clients.append(client)
                except Exception as e:
                    pass
            self.clients = new_clients

    def exposed_login(self, username, conn, callbacks):
        with self.lock:
            if self.game_started:
                for client in self.clients:
                    if client["username"] == username:
                        self.exposed_relogin(username, conn, callbacks)
                        return LoginResult.SUCCESS
                return LoginResult.GAME_STARTED
            for client in self.clients:
                if client["username"] == username:
                    return LoginResult.USERNAME_IN_USE
            self.clients.append(
                {
                    "conn": conn,
                    "callbacks": callbacks,
                    "username": username,
                }
            )
            self.total_players += 1
            print(f"Adding client: {username}")
            return LoginResult.SUCCESS

    def exposed_relogin(self, username, conn, callbacks):
        with self.lock:
            self.clients.append(
                {
                    "conn": conn,
                    "callbacks": callbacks,
                    "username": username,
                }
            )
            print(f"Client {username} reconnected")
            return self.player_scores

    def exposed_betray(self, username, betray):
        self.player_actions[username] = betray
        if len(self.player_actions) == self.total_players:
            self.next_turn()

    def next_turn(self):
        last_round = False
        if self.current_round == self.total_rounds:
            last_round = True

        self.turn_log = {
            "scores": {"a": 1, "b": 2, "c": 3},
            "round": self.current_round,
            "actions": self.player_actions,
        }
        self.player_actions = {}
        threads = []
        for client in self.clients:
            thread = threading.Thread(
                target=self._execute_callback,
                args=(client, "next_turn", [self.turn_log, last_round]),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.current_round += 1

    def end_game(self):
        print("Ending game...")
        self.game_started = False
        threads = []
        for client in self.clients:
            thread = threading.Thread(
                target=self._execute_callback,
                args=(client, "end_game", []),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def start_game(self):
        print("Starting game...")
        self.game_started = True
        threads = []
        for client in self.clients:
            thread = threading.Thread(
                target=self._execute_callback,
                args=(client, "start_game", [self.clients]),
            )
            threads.append(thread)
            thread.start()
            client["screen"] = GameState.PLAYING
        for thread in threads:
            thread.join()

    def _execute_callback(self, client, callback_name, parameters=None):
        try:
            client["callbacks"][callback_name](*parameters)
        except Exception as e:
            print(f"Failed to contact a client: {e}")


server = None


def start_server():
    global server
    service = MyService()
    server = ThreadedServer(
        service, port=12345, protocol_config={"allow_all_attrs": True}
    )
    server.start()


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    input("Press Enter to  start game...")
    server.service.start_game()

    input("Press Enter to exit...")
    server.close()
    server_thread.join()
