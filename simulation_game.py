import numpy as np
import random
from collections import defaultdict, deque
import game2  #Import the game2 module, which handles individual game rounds

#Player class represents each player in the game and their decision-making and resource management logic.
class Player:
    def __init__(self, id, n_players, alpha=0.1, gamma=0.9, history_length=10, betray_probability=0.5):
        """
        Initialize a Player instance with Q-learning parameters and other properties.

        Args:
        - id: Unique identifier for the player.
        - n_players: Total number of players in the game.
        - alpha: Learning rate for Q-learning (controls how fast the player updates).
        - gamma: Discount factor for future rewards in Q-learning.
        - history_length: Length of the history of interactions between the players.
        - betray_probability: Initial probability of betrayal (0 means always cooperate, 1 means always betray).
        """
        self.id = id  #Unique player ID
        self.n_players = n_players  #Total number of players in the game
        self.alpha = alpha  #Learning rate for Q-learning
        self.gamma = gamma  #Discount factor for future rewards in Q-learning
        self.q_table = {}  #Q-table for storing state-action values
        self.history = defaultdict(lambda: deque(maxlen=history_length))  #History of interactions
        self.betray_probability = betray_probability  #Probability of betrayal (starts at the provided value)
        self.total_resources = 0  #Total resources the player has accumulated

    def get_state(self, resources):
        """
        Calculate the relative state of the player compared to the resources of other players.

        Args:
        - resources: A list of the current resources of all players.

        Returns:
        - A tuple representing the relative difference in resources between the current player and others.
        """
        relative_resources = tuple(res - resources[self.id] for res in resources)
        return relative_resources

    def choose_action(self, state, target_player, round_num):
        """
        Decide whether to betray or cooperate with another player.

        Args:
        - state: The current state of the game (resources of players).
        - target_player: The player who is being targeted for betrayal or cooperation.
        - round_num: The current round number.

        Returns:
        - The target player's ID (as a string) if betraying, or None if cooperating.
        """
        if random.uniform(0, 1) < self.betray_probability:  #Random decision based on betrayal probability
            return str(target_player)  #Betray the target player
        else:
            return None  #Cooperate (no betrayal)

    def increase_intensity(self):
        """
        Increase the player's probability of betrayal to make them more aggressive in future rounds.
        """
        self.betray_probability = min(1.0, self.betray_probability + 0.05)

    def update_history(self, target_player, action):
        """
        Update the player's interaction history with the target player.

        Args:
        - target_player: The player who was the target of the action.
        - action: The action taken (betrayal or cooperation).
        """
        self.history[target_player].append(1 if action is not None else 0)  #1 for betrayal, 0 for cooperation

    def update_q_table(self, state, action, reward, new_state):
        """
        Update the Q-table based on the outcome of the action taken in the game.

        Args:
        - state: The previous state before the action.
        - action: The action taken by the player.
        - reward: The reward received after taking the action.
        - new_state: The state after the action.
        """
        #Initialize Q-values if the state is new
        if state not in self.q_table:
            self.q_table[state] = {str(player): 0 for player in range(self.n_players) if player != self.id}
            self.q_table[state][None] = 0  #Option for cooperation
        if new_state not in self.q_table:
            self.q_table[new_state] = {str(player): 0 for player in range(self.n_players) if player != self.id}
            self.q_table[new_state][None] = 0  #Option for cooperation

        q_predict = self.q_table[state][action]  #Get the predicted Q-value for the action
        q_target = reward + self.gamma * max(self.q_table[new_state].values())  #Calculate the target Q-value

        #Update the Q-value using the Q-learning update formula
        self.q_table[state][action] += self.alpha * (q_target - q_predict)


#Game class represents the overall game logic and coordinates player actions and round outcomes.
class Game:
    def __init__(self, n_players, n_resources, betray_probabilities):
        """
        Initialize the Game instance.

        Args:
        - n_players: Total number of players.
        - n_resources: Initial resources for each player.
        - betray_probabilities: List of initial betrayal probabilities for each player.
        """
        self.n_players = n_players  #Number of players
        self.n_resources = n_resources  #Initial resources per player
        #Create players with their respective betrayal probabilities
        self.players = [
            Player(i, n_players, betray_probability=betray_probabilities[i]) 
            for i in range(n_players)
        ]
        self.resources = np.full(n_players, n_resources)  #Initialize all players' resources to the starting amount
        self.betrayal_log = []  #Log of all betrayals that occurred
        self.total_points = {str(i): 0 for i in range(n_players)}  #Initialize total points/resources for all players

    def reset(self):
        """
        Reset the game state to its initial configuration, including resources and logs.
        """
        self.resources = np.full(self.n_players, self.n_resources)  # Reset resources to initial value
        self.betrayal_log = []  # Clear the betrayal log
        self.total_points = {str(i): 0 for i in range(self.n_players)}  # Reset total points for all players

    def has_winner(self):
        """
        Check if there is a single player with the most resources (i.e., the winner).

        Returns:
        - True if there is a clear winner, False otherwise.
        """
        max_resources = max(self.total_points.values())
        return list(self.total_points.values()).count(max_resources) == 1

    def check_for_tie(self):
        """
        Check if there is a tie (multiple players have the highest resources).

        Returns:
        - True if there is a tie, False otherwise.
        """
        max_resources = max(self.total_points.values())
        return list(self.total_points.values()).count(max_resources) > 1

    def play_round(self, round_num):
        """
        Play one round of the game where players choose actions (betray or cooperate).

        Args:
        - round_num: The current round number.
        """
        state = tuple(self.resources)  #Capture the current state of resources
        actions = {}  #Store each player's action (betrayal/cooperation)

        #Each player selects a target and chooses an action (betray or cooperate)
        for player in self.players:
            target_player = random.choice([i for i in range(self.n_players) if i != player.id])
            relative_state = player.get_state(self.resources)
            action = player.choose_action(relative_state, target_player, round_num)
            actions[str(player.id)] = action
            player.update_history(target_player, action)

        #Use the game2 module to process the round and update total points
        results, self.total_points = game2.play_turn(actions, self.total_points, self.n_resources)

        #Update each player's Q-table and resources based on the results of the round
        for player in self.players:
            player_id = str(player.id)
            _, turn_points, total_points = results[player_id]
            player.total_resources = total_points  #Update player's total resources
            new_state = player.get_state(list(self.total_points.values()))
            player.update_q_table(state, actions[player_id], turn_points, new_state)

        #Log the betrayals that occurred in this round
        betrayals = [(player_id, action) for player_id, action in actions.items() if action is not None]
        self.betrayal_log.append((round_num, betrayals))

    def play_game(self, n_rounds):
        """
        Play the game for a specified number of rounds or until a single winner is found.

        Args:
        - n_rounds: The maximum number of rounds to play.

        Returns:
        - A list of total resources for each player at the end of the game.
        """
        #First, play all the specified rounds
        for round_num in range(1, n_rounds + 1):
            self.play_round(round_num)

        #After all rounds, if there's a tie, continue playing rounds until a winner is found
        while self.check_for_tie():
            n_rounds += 1
            print(f"Round {n_rounds}: Continuing due to tie...")
            self.play_round(n_rounds)
            #Increase each player's intensity (likelihood to betray) in tie rounds
            for player in self.players:
                player.increase_intensity()

        return [player.total_resources for player in self.players]

    def display_betrayal_log(self):
        """
        Print the log of all betrayals that occurred during the game.
        """
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
        """
        Print the final results of the game, showing the winner and all players' resources.
        """
        print("\nFinal Results:")
        total_resources = [(int(player_id), resources) for player_id, resources in self.total_points.items()]
        sorted_players = sorted(total_resources, key=lambda x: x[1], reverse=True)  # Sort players by resources
        for i, (player_id, resource) in enumerate(sorted_players):
            if i == 0:
                print(f"Winner: Player {player_id} finished with {resource} resources")
            else:
                print(f"Player {player_id} finished with {resource} resources")


if __name__ == "__main__":
    #Set game parameters
    n_players = 5
    n_resources = 2
    n_rounds = 100  #Number of rounds to play

    #Initial betrayal probabilities for each player
    betray_probabilities = [0.5, 0.5, 0.5, 0.5, 0.5]  # All players start with cooperation

    #Initialize and play the game
    game_instance = Game(n_players, n_resources, betray_probabilities)

    #Play the specified number of rounds
    game_instance.play_game(n_rounds)

    #Display the betrayal log
    game_instance.display_betrayal_log()

    #Display Q-tables and interaction histories for each player
    for i, player in enumerate(game_instance.players):
        print(f"Player {i} Final Q-Table:")
        for state, actions in player.q_table.items():
            print(f"State {state}: {actions}")
        print(f"Player {i} Interaction History with Other Players:")
        for target, history in player.history.items():
            print(f"With Player {target}: {list(history)}")
        print()

    #Display final results
    game_instance.display_final_results()
