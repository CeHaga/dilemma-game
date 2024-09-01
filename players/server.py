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

    def on_connect(self, conn):
        print("Client connected")

    def on_disconnect(self, conn):
        print("Client disconnected")

        for client in self.clients:
            try:
                client["callbacks"]["is_alive"]()
            except Exception as e:
                self.clients.remove(client)

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

    def start_game(self):
        print("Starting game...")
        self.game_started = True
        threads = []
        for client in self.clients:
            thread = threading.Thread(
                target=self._execute_callback, args=(client, "start_game")
            )
            threads.append(thread)
            thread.start()

    def _execute_callback(self, client, callback_name):
        try:
            client["callbacks"][callback_name](self.clients)
        except Exception as e:
            print(f"Failed to contact client {client['username']}:\n{e}")


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
