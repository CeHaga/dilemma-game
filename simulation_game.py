import numpy as np
import random
from collections import defaultdict, deque
import game2  #Import the game2 module to handle individual game rounds

#Player class represents individual players in the game
class Player:
    def __init__(self, id, n_players, betray_probability, alpha=0.5, gamma=0.5):
        """
        Initialize the player with a unique ID, Q-learning parameters, and betrayal probability.
        
        Args:
        - id: Unique player ID.
        - n_players: Total number of players in the game.
        - betray_probability: Initial probability of betrayal.
        
        - alpha: If alpha is close to 1, the agent learns quickly, meaning it heavily weighs new information and quickly updates its Q-values.
        If alpha is close to 0, the agent learns slowly, meaning it gives more weight to past experiences and adjusts its Q-values more gradually.
        
        - gamma: This is the discount factor. It determines how much importance is given to future rewards compared to immediate rewards. A gamma close to 1 means future rewards are valued similarly to immediate rewards, while a gamma closer to 0 means the player is more short-sighted, prioritizing immediate rewards.
        """
        self.id = id  #Unique player ID
        self.n_players = n_players  #Total number of players in the game
        self.alpha = alpha  #Learning rate for Q-learning
        self.gamma = gamma  #Discount factor for future rewards
        
        #Initialize the Q-table with optimistic values, favoring betrayal initially
        self.q_table = defaultdict(lambda: {None: 0.5, **{str(target): betray_probability * 1.0 for target in range(n_players) if target != self.id}})
        
        #Store past interactions (cooperate/betray) with other players
        self.history = defaultdict(lambda: deque())  
        self.betray_probability = betray_probability  #The probability of betrayal for the player
        self.total_resources = 0  #Track the total resources accumulated by the player

    def get_state(self, resources):
        """
        Get the player's current state in relation to other players' resources.
        
        Args:
        - resources: List of resources for all players.
        
        Returns:
        - relative_resources: Resources of other players relative to the current player.
        """
        relative_resources = tuple(res - resources[self.id] for res in resources)
        return relative_resources

    def choose_action(self, state, target_player, round_num):
        """
        Choose whether to betray or cooperate with the target player.
        
        Args:
        - state: The player's current state.
        - target_player: The player being targeted for betrayal or cooperation.
        - round_num: The current round number in the game.

        Returns:
        - str(target_player): Betray the target player.
        - None: Cooperate with the target player.
        """
        if round_num == 1:  #First round, rely on initial betrayal probability
            if random.uniform(0, 1) < self.betray_probability:
                return str(target_player)  #Choose to betray the target player
            else:
                return None  #Choose to cooperate
        else:
            #For subsequent rounds, use Q-values to decide (Q-learning based decision)
            q_value_cooperate = self.q_table[state].get(None, 0.5)  #Q-value for cooperation
            q_value_betray = self.q_table[state].get(str(target_player), self.betray_probability)  #Q-value for betrayal
            #Calculate the betrayal chance, biased by the betrayal probability
            betrayal_chance = self.betray_probability * (q_value_betray - q_value_cooperate)
            betrayal_chance = max(betrayal_chance, 0.1)  #Ensure a minimum betrayal chance
            if random.uniform(0, 1) < betrayal_chance:
                return str(target_player)  #Betray the target player
            else:
                return None  #Cooperate

    def increase_intensity(self):
        """
        Increase the intensity of betrayal by slightly increasing the player's betrayal probability.
        """
        #Cap the betrayal probability at 1.0
        self.betray_probability = min(1.0, self.betray_probability + 0.05)  

    def update_history(self, target_player, action):
        """
        Update the player's interaction history with another player.
        
        Args:
        - target_player: The player targeted for betrayal or cooperation.
        - action: The action taken (betrayal or cooperation).
        """
        #1 if betrayed, 0 if cooperated
        self.history[target_player].append(1 if action is not None else 0)  

    def update_q_table(self, state, action, reward, new_state):
        """
        Update the player's Q-table based on the action taken and the reward received.
        
        Args:
        - state: The player's state before the action.
        - action: The action taken (betrayal or cooperation).
        - reward: The reward received after taking the action.
        - new_state: The state after the action was taken.
        """
        #Initialize new states in the Q-table if they don't already exist
        if state not in self.q_table:
            self.q_table[state] = {str(player): self.betray_probability for player in range(self.n_players) if player != self.id}
            self.q_table[state][None] = 0.5  #Default Q-value for cooperation

        if new_state not in self.q_table:
            self.q_table[new_state] = {str(player): self.betray_probability for player in range(self.n_players) if player != self.id}
            self.q_table[new_state][None] = 0.5  #Default Q-value for cooperation

        #Q-learning update rule
        q_predict = self.q_table[state][action]  #Get the predicted Q-value for the action
        
        #Calculate the target Q-value
        q_target = reward + self.gamma * max(self.q_table[new_state].values())  
        self.q_table[state][action] += self.alpha * (q_target - q_predict)  #Update the Q-value

#Game class represents the overall game and handles rounds between multiple players
class Game:
    def __init__(self, n_players, n_resources, betray_probabilities):
        """
        Initialize the game with the given number of players, resources, and betrayal probabilities.
        
        Args:
        - n_players: Total number of players.
        - n_resources: Initial resources for each player.
        - betray_probabilities: List of initial betrayal probabilities for each player.
        """
        self.n_players = n_players  #Number of players in the game
        self.n_resources = n_resources  #Initial resources per player
        self.players = [Player(i, n_players, betray_probability=betray_probabilities[i]) for i in range(n_players)]  #Initialize each player
        self.resources = np.full(n_players, n_resources)  #Initialize resources for all players
        self.betrayal_log = []  #Log betrayals during the game
        
        #Track total points/resources of each player
        self.total_points = {str(i): 0 for i in range(n_players)}  
        self.collapse_count = 0  #Track how many times the system collapsed
        
        #Track contributions to system collapse
        self.collapse_contributions = {str(i): 0 for i in range(n_players)}  

    def reset(self):
        """
        Reset the game state to the initial conditions (useful for starting a new game).
        """
        #Reset resources for all players
        self.resources = np.full(self.n_players, self.n_resources)  
        self.betrayal_log = []  #Clear the betrayal log
        self.total_points = {str(i): 0 for i in range(self.n_players)}  #Reset total points
        self.collapse_count = 0  #Reset collapse count
        
        #Reset collapse contributions
        self.collapse_contributions = {str(i): 0 for i in range(self.n_players)}  

    def play_round(self, round_num):
        """
        Simulate a single round of the game where all players decide whether to betray or cooperate.
        """
        state = tuple(self.resources)  #Current state of the game (resources of all players)
        actions = {}  #Dictionary to store each player's action (betray or cooperate)
        round_rewards = defaultdict(int)  #Track rewards for each player in the current round

        #Each player selects a target and chooses whether to betray or cooperate
        for player in self.players:
            if not player.history:  
                #In the first round, choose a random target (no history available)
                target_player = random.choice([i for i in range(self.n_players) if i != player.id])  
            else:
                #In subsequent rounds, choose a target based on history (most betrayed player)
                target_player = max(player.history, key=lambda t: sum(player.history[t]))  

            relative_state = player.get_state(self.resources)  #Get the player's current state
            
            #Choose whether to betray or cooperate
            action = player.choose_action(relative_state, target_player, round_num)  
            actions[str(player.id)] = action  #Store the player's action
            player.update_history(target_player, action)  #Update the player's history

        #Process the round using the game2 module (handle betrayals, cooperation, and collapses)
        results, self.total_points, betrayals, collapse_occurred = game2.play_turn(actions, self.total_points, self.n_resources)

        #If the system collapsed, update collapse contributions
        if collapse_occurred:
            self.collapse_count += 1
            for betrayed, betrayers in betrayals.items():
                #Collapse happens if a player is betrayed by more than 2 others (Change to if collapse_occurred)
                if len(betrayers) > 2:  
                    for betrayer in betrayers:
                        #Track contributions to collapse
                        self.collapse_contributions[betrayer] += 1  

        #Update each player's Q-table and resources based on the results of the round
        for player in self.players:
            player_id = str(player.id)
            _, turn_points, total_points = results[player_id]  #Get the result for the player
            player.total_resources = total_points  #Update player's total resources
            new_state = player.get_state(list(self.total_points.values()))  #Get the new state
            reward = round_rewards[player_id]  #Reward based on the player's actions
            
            #Update the Q-table
            player.update_q_table(state, actions[player_id], reward, new_state)  

        #Log betrayals for the round
        self.betrayal_log.append((round_num, [(betrayer, betrayed) for betrayed, betrayers in betrayals.items() for betrayer in betrayers]))

    def play_game(self, n_rounds):
        """
        Play the game for a fixed number of rounds.
        """
        for round_num in range(1, n_rounds + 1):
            self.play_round(round_num)  #Simulate each round
        
        #Return the total resources of each player
        return [player.total_resources for player in self.players]  

    def display_betrayal_log(self):
        """
        Display a log of all the betrayals that occurred during the game.
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
        Display the final results of the game, including system collapse information.
        """
        print(f"\nThe system collapsed {self.collapse_count} times.")
        for player_id, count in self.collapse_contributions.items():
            print(f"Player {player_id} contributed to the system collapsing {count} times.")

        #Display the final results for each player
        print("\nFinal Results:")
        total_resources = [(int(player_id), resources) for player_id, resources in self.total_points.items()]
        sorted_players = sorted(total_resources, key=lambda x: x[1], reverse=True)
        for i, (player_id, resource) in enumerate(sorted_players):
            if i == 0:
                print(f"Winner: Player {player_id} finished with {resource} resources")
            else:
                print(f"Player {player_id} finished with {resource} resources")


# Main block to set up and run the game
if __name__ == "__main__":
    n_players = 5  #Number of players
    n_resources = 2  #Initial resources per player
    n_rounds = 10000  #Number of rounds to play

    #Initial betrayal probabilities for each player
    betray_probabilities = [0.5, 0.5, 0.5, 0.5, 1.0]

    #Initialize and play the game
    game_instance = Game(n_players, n_resources, betray_probabilities)

    #Play the specified number of rounds
    game_instance.play_game(n_rounds)

    #Display the betrayal log
    game_instance.display_betrayal_log()

    #Display the final results
    game_instance.display_final_results()
