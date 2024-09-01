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
        self.total_rounds = 10
        self.current_round = 1

    def on_connect(self, conn):
        print("Client connected")

    def on_disconnect(self, conn):
        print("Client disconnected")
        new_clients = []
        for client in self.clients:
            try:
                client["callbacks"]["is_alive"]()
                new_clients.append(client)
            except Exception as e:
                pass
        self.clients = new_clients

    def exposed_login(self, username, conn, callbacks):
        if self.game_started:
            return LoginResult.GAME_STARTED
        for client in self.clients:
            if client["username"] == username:
                return LoginResult.USERNAME_IN_USE
        self.clients.append(
            {"conn": conn, "callbacks": callbacks, "username": username}
        )
        print(f"Adding client: {username}")
        return LoginResult.SUCCESS

    def exposed_betray(self, username, betray):
        self.player_actions[username] = betray
        if len(self.player_actions) == len(self.clients):
            self.next_turn()

    def next_turn(self):
        print(f"Player actions: {self.player_actions}")
        player_scores = {}
        self.player_actions = {}
        threads = []
        for client in self.clients:
            thread = threading.Thread(
                target=self._execute_callback,
                args=(client, "next_turn", [player_scores]),
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
