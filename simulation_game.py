import numpy as np
import random
from collections import defaultdict, deque
import game2  # Import the game2 module to handle individual game rounds

class Player:
    def __init__(self, id, n_players, betray_probability, alpha=0.5, gamma=0.5):
        self.id = id
        self.n_players = n_players
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = defaultdict(lambda: {None: 0.5, **{str(target): betray_probability * 1.0 for target in range(n_players) if target != self.id}})
        self.history = defaultdict(lambda: deque())
        self.betray_probability = betray_probability
        self.total_resources = 0
        self.betray_count = 0

    def choose_action(self, state, target_player, round_num):
        if round_num == 1:
            if random.uniform(0, 1) < self.betray_probability:
                return str(target_player)
            else:
                return None
        else:
            q_value_cooperate = self.q_table[state].get(None, 0.5)
            q_value_betray = self.q_table[state].get(str(target_player), self.betray_probability)
            betrayal_chance = self.betray_probability * (q_value_betray - q_value_cooperate)
            betrayal_chance = max(betrayal_chance, 0.1)
            if random.uniform(0, 1) < betrayal_chance:
                return str(target_player)
            else:
                return None

    def update_history(self, target_player, action):
        self.history[target_player].append(1 if action is not None else 0)
        if action is not None:
            self.betray_count += 1

class Game:
    def __init__(self, n_players, n_resources, betray_probabilities):
        self.n_players = n_players
        self.n_resources = n_resources
        self.players = [Player(i, n_players, betray_probability=betray_probabilities[i]) for i in range(n_players)]
        self.resources = np.full(n_players, n_resources)
        self.betrayal_log = []
        self.total_points = {str(i): 0 for i in range(n_players)}
        self.collapse_count = 0
        self.collapse_contributions = {str(i): 0 for i in range(n_players)}

    def choose_target(self, player):
        if not player.history:
            return random.choice([i for i in range(self.n_players) if i != player.id])
        else:
            return max(player.history, key=lambda t: sum(player.history[t]))

    def play_round(self, round_num):
        state = tuple(self.resources)
        actions = {}
        betrayals = defaultdict(list)

        for player in self.players:
            target_player = self.choose_target(player)
            action = player.choose_action(state, target_player, round_num)
            actions[str(player.id)] = action
            if action is not None:
                betrayals[action].append(str(player.id))

        results, self.total_points, _, collapse_occurred = game2.play_turn(actions, self.total_points, self.n_resources)

        return {
            'actions': actions,
            'resources': self.total_points,
            'betrayals': dict(betrayals)
        }
