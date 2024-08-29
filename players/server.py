import rpyc
from rpyc.utils.server import ThreadedServer
from game import play_turn
import threading

class GameService(rpyc.Service):
    def __init__(self):
        self.players = {}
        self.game_started = False
        self.lock = threading.Lock()

    def exposed_add_connection(self, name, conn):
        with self.lock:
            print('c')
            if self.game_started:
                print(f"{name} tried to connect after game started")
                return None
            if name in self.players.keys():
                print(f'{name} already used')
                return False
            print(f"New connection from {name}")
            self.players[name] = conn
            print('d')
            return True

    def exposed_remove_connection(self, name):
        with self.lock:
            print('e')
            del self.players[name]
            print('f')

    def __str__(self) -> str:
        with self.lock:
            print('g')
            return str(self.players)

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
    print(gs)
    print(gs.players)
    gs.print_players()
    print('b')

    stop_server()
    thread.join()
