from enum import Enum


class GameState(Enum):
    WAITING_FOR_PLAYERS = 0
    PLAYING = 1
    WAITING_SELECT = 2

    def __eq__(self, other):
        return self.value == other.value


class LoginResult(Enum):
    SUCCESS = 0
    USERNAME_IN_USE = 1
    GAME_STARTED = 2
    WRONG_IP = 3

    def __eq__(self, other):
        return self.value == other.value
