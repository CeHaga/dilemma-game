import numpy as np
import random
from collections import defaultdict, deque
import game2  # Import the game2 module to handle individual game rounds

# Player class represents individual players in the game
class Player:
    def __init__(self, id, n_players, betray_probability, alpha=0.5, gamma=0.5):
        self.id = id  # Unique player ID
        self.n_players = n_players  # Total number of players in the game
        self.alpha = alpha  # Learning rate for Q-learning
        self.gamma = gamma  # Discount factor for future rewards
        self.q_table = defaultdict(lambda: {None: 0.5, **{str(target): betray_probability * 1.0 for target in range(n_players) if target != self.id}})
        self.history = defaultdict(lambda: deque())  
        self.betray_probability = betray_probability  # The probability of betrayal for the player
        self.total_resources = 0  # Track the total resources accumulated by the player
        self.betray_count = 0  # Track the total number of betrayals by the player

    def get_state(self, resources):
        relative_resources = tuple(res - resources[self.id] for res in resources)
        return relative_resources

    def choose_action(self, state, target_player, round_num):
        if round_num == 1:  # First round, rely on initial betrayal probability
            if random.uniform(0, 1) < self.betray_probability:
                return str(target_player)  # Choose to betray the target player
            else:
                return None  # Choose to cooperate
        else:
            q_value_cooperate = self.q_table[state].get(None, 0.5)  # Q-value for cooperation
            q_value_betray = self.q_table[state].get(str(target_player), self.betray_probability)  # Q-value for betrayal
            betrayal_chance = self.betray_probability * (q_value_betray - q_value_cooperate)
            betrayal_chance = max(betrayal_chance, 0.1)  # Ensure a minimum betrayal chance
            if random.uniform(0, 1) < betrayal_chance:
                return str(target_player)  # Betray the target player
            else:
                return None  # Cooperate

    def increase_intensity(self):
        self.betray_probability = min(1.0, self.betray_probability + 0.05)

    def update_history(self, target_player, action):
        self.history[target_player].append(1 if action is not None else 0)
        if action is not None:
            self.betray_count += 1  # Increment betrayal count if the player betrayed

    def update_q_table(self, state, action, reward, new_state):
        if state not in self.q_table:
            self.q_table[state] = {str(player): self.betray_probability for player in range(self.n_players) if player != self.id}
            self.q_table[state][None] = 0.5  # Default Q-value for cooperation
        if new_state not in self.q_table:
            self.q_table[new_state] = {str(player): self.betray_probability for player in range(self.n_players) if player != self.id}
            self.q_table[new_state][None] = 0.5  # Default Q-value for cooperation
        q_predict = self.q_table[state][action]  # Get the predicted Q-value for the action
        q_target = reward + self.gamma * max(self.q_table[new_state].values())  
        self.q_table[state][action] += self.alpha * (q_target - q_predict)  # Update the Q-value

class Game:
    def __init__(self, n_players, n_resources, betray_probabilities):
        self.n_players = n_players
        self.n_resources = n_resources
        self.players = [Player(i, n_players, betray_probability=betray_probabilities[i]) for i in range(n_players)]
        self.resources = np.full(n_players, n_resources)
        self.betrayal_log = []  # Log betrayals during the game
        self.total_points = {str(i): 0 for i in range(n_players)}
        self.collapse_count = 0
        self.collapse_contributions = {str(i): 0 for i in range(n_players)}

    def reset(self):
        self.resources = np.full(self.n_players, self.n_resources)
        self.betrayal_log = []
        self.total_points = {str(i): 0 for i in range(self.n_players)}
        self.collapse_count = 0
        self.collapse_contributions = {str(i): 0 for i in range(self.n_players)}

    def play_round(self, round_num):
        state = tuple(self.resources)
        actions = {}
        round_rewards = defaultdict(int)

        for player in self.players:
            if not player.history:
                target_player = random.choice([i for i in range(self.n_players) if i != player.id])  
            else:
                target_player = max(player.history, key=lambda t: sum(player.history[t]))  
            relative_state = player.get_state(self.resources)
            action = player.choose_action(relative_state, target_player, round_num)
            actions[str(player.id)] = action
            player.update_history(target_player, action)

        results, self.total_points, betrayals, collapse_occurred = game2.play_turn(actions, self.total_points, self.n_resources)

        if collapse_occurred:
            self.collapse_count += 1
            for betrayed, betrayers in betrayals.items():
                if len(betrayers) > 2:  
                    for betrayer in betrayers:
                        self.collapse_contributions[betrayer] += 1  

        for player in self.players:
            player_id = str(player.id)
            _, turn_points, total_points = results[player_id]
            player.total_resources = total_points
            new_state = player.get_state(list(self.total_points.values()))
            reward = round_rewards[player_id]
            player.update_q_table(state, actions[player_id], reward, new_state)
        self.betrayal_log.append((round_num, [(betrayer, betrayed) for betrayed, betrayers in betrayals.items() for betrayer in betrayers]))

    def play_game(self, n_rounds):
        for round_num in range(1, n_rounds + 1):
            self.play_round(round_num)
        return [player.total_resources for player in self.players]  

    def display_betrayal_log(self):
        print("\nBetrayal Log for this Game:")
        for round_num, betrayals in self.betrayal_log:
            print(f"Round {round_num}:")
            if betrayals:
                for betrayer, betrayed in betrayals:
                    print(f"Player {betrayer} betrayed Player {betrayed}")
            else:
                print("No betrayals")
        print()

    def display_final_results(self):
        print(f"\nThe system collapsed {self.collapse_count} times.")
        for player_id, count in self.collapse_contributions.items():
            print(f"Player {player_id} contributed to the system collapsing {count} times.")

        print("\nFinal Results:")
        total_resources = [(int(player_id), resources) for player_id, resources in self.total_points.items()]
        sorted_players = sorted(total_resources, key=lambda x: x[1], reverse=True)

        # Calculate betrayal percentages for each player
        for player in self.players:
            betrayal_percentage = (player.betray_count / len(self.betrayal_log)) * 100 if len(self.betrayal_log) > 0 else 0
            print(f"Player {player.id} betrayed {player.betray_count} times, Betrayal Percentage: {betrayal_percentage:.2f}%")

        for i, (player_id, resource) in enumerate(sorted_players):
            if i == 0:
                print(f"Winner: Player {player_id} finished with {resource} resources")
            else:
                print(f"Player {player_id} finished with {resource} resources")


if __name__ == "__main__":
    n_players = 5
    n_resources = 2
    n_rounds = 100

    betray_probabilities = [0.5, 0.5, 0.5, 0.5, 1.0]

    game_instance = Game(n_players, n_resources, betray_probabilities)

    game_instance.play_game(n_rounds)
    game_instance.display_betrayal_log()
    game_instance.display_final_results()
