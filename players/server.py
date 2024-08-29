import rpyc
from rpyc.utils.server import ThreadedServer
from game import play_turn
import threading

class GameService(rpyc.Service):
    def __init__(self):
        self.players = {}
        self.connections = []
        self.game_started = False
        self.lock = threading.Lock()

    def on_connect(self, conn):
        with self.lock:
            if self.game_started:
                conn.close()
                return
            self.players[conn] = None

    def exposed_login(self, player_name, conn):
        with self.lock:
            if player_name not in self.players.values():
                self.players[conn] = player_name
                self.notify_all_clients(f"{player_name} has joined the game")
                return True
            return False

    def notify_all_clients(self, message):
        for conn in self.players.keys():
            try:
                conn.root.receive_message(message)
            except:
                if conn in self.players:
                    del self.players[conn]

    def start_game(self):
        with self.lock:
            self.game_started = True
            self.notify_all_clients("Game has started!")
            return True

server = None
gs = None

def run_server(host="localhost", port=12345):
    global server, gs
    gs = GameService()
    server = ThreadedServer(gs, hostname=host, port=port, protocol_config={'allow_public_attrs': True})
    print(f"Server listening on {host}:{port}")
    server.start()

def stop_server():
    global server
    server.close()

if __name__ == "__main__":
    thread = threading.Thread(target=run_server)
    thread.start()

    input("Pressione Enter para começar...")
    print('a')
    gs.start_game()
    print('b')

    stop_server()
    thread.join()
