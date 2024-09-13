#random: Used for generating random numbers.
#defaultdict: Provides default values for dictionary keys that don't exist.
#deque: Used to efficiently append and pop from both ends of a collection.
import numpy as np
import random
from collections import defaultdict, deque

#Class representing a Player in the game.
class Player:
    '''
    #Constructor for initializing player properties.
        id: Unique identifier for the player.
        n_players: Total number of players in the game.
        betray_probability: Probability of betraying another player.
        alpha: Learning rate for Q-learning algorithm (default 1.0).
        gamma: Discount factor for future rewards in Q-learning (default 0.01).
    '''
    def __init__(self, id, n_players, betray_probability, alpha=1.0, gamma=0.01):
        #Assign unique player ID and number of players in the game.
        self.id = id
        self.n_players = n_players
        
        #Initialize Q-learning parameters (alpha, gamma).
        self.alpha = alpha
        self.gamma = gamma
        
        ''' 
            Q-table where each state-action pair is stored.
            The state is represented as a dictionary with keys being player IDs (actions) and values being Q-values.
            Default Q-value for cooperation (None) is set to 0.5, and for betrayal, it's based on betray_probability.
        '''
        self.q_table = defaultdict(
            lambda: {
                None: 0.5,
                **{
                    str(target): betray_probability * 1.0
                    for target in range(n_players)
                    if target != self.id
                },
            }
        )
        
        #History of player actions, stored using a deque to efficiently track past actions.
        self.history = defaultdict(lambda: deque())
        
        #Probability with which this player will betray others.
        self.betray_probability = betray_probability
        
        #Total resources this player has accumulated during the game.
        self.total_resources = 0
        
        #Count of how many times this player has betrayed others.
        self.betray_count = 0
    '''
    #Method to choose an action during a specific round.
        state: Current state of the game (resources of each player).
        target_player: Player this player may target for betrayal.
        round_num: Current round number.
    '''
    def choose_action(self, state, target_player, round_num):
        #In the first round, the action is based on a random check against betray_probability.
        if round_num == 1:
            if random.uniform(0, 1) < self.betray_probability:
                return str(target_player)
            else:
                return None
        else:
            #Q-values for cooperation and betrayal actions are fetched from the Q-table.
            q_value_cooperate = self.q_table[state].get(None, 0.5)
            q_value_betray = self.q_table[state].get(
                str(target_player), self.betray_probability
            )
            
            #Calculate the chance of betrayal based on the Q-values and betray_probability.
            betrayal_chance = self.betray_probability * (
                q_value_betray - q_value_cooperate
            )
            
            #Ensure the betrayal chance is at least 0.1 to encourage exploration.
            betrayal_chance = max(betrayal_chance, 0.1)
            
            #Use the betrayal chance to decide whether to betray the target or cooperate.
            if random.uniform(0, 1) < betrayal_chance:
                return str(target_player)
            else:
                return None

    '''
    #Method to update the player's history after taking an action.
        target_player: The player who was targeted by the action.
        action: The action taken (None for cooperation, player ID for betrayal).
    '''
    def update_history(self, target_player, action):
        #Record the action (1 for betrayal, 0 for cooperation) in the target player's history.
        self.history[target_player].append(1 if action is not None else 0)
        
        #If the action was betrayal, increment the betrayal count for this player.
        if action is not None:
            self.betray_count += 1

    '''
    #Method to update the Q-table using the Q-learning algorithm.
        state: The state before the action was taken.
        action: The action taken (None for cooperation, player ID for betrayal).
        reward: The reward received for the action.
        new_state: The state after the action was taken.
    '''
    def update_q_table(self, state, action, reward, new_state):
        #Fetch the current Q-value for the state-action pair.
        current_q = self.q_table[state][action]
        
        #Calculate the maximum Q-value for the new state to determine the best future action.
        max_future_q = max(self.q_table[new_state].values())
        
        #Update the Q-value using the Q-learning update rule.
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)
        
        #Store the updated Q-value in the Q-table.
        self.q_table[state][action] = new_q

#Class representing the overall game with multiple players.
class Game:
    '''
    #Constructor to initialize the game state.
        n_players: Total number of players in the game.
        n_resources: Number of resources each player starts with.
        betray_probabilities: List of betrayal probabilities for each player.
        play_turn_func: The function that simulates a turn in the game.
    '''
    def __init__(self, n_players, n_resources, betray_probabilities, play_turn_func):
        self.n_players = n_players
        self.n_resources = n_resources
        
        #Create a list of Player objects, each with a unique ID and betrayal probability.
        self.players = [
            Player(i, n_players, betray_probability=betray_probabilities[i])
            for i in range(n_players)
        ]
        
        #Initialize resources for each player.
        self.resources = np.full(n_players, n_resources)
        
        #Log to keep track of betrayals during the game.
        self.betrayal_log = []
        
        #Dictionary to keep track of each player's total points.
        self.total_points = {str(i): 0 for i in range(n_players)}
        
        #Count of how many times a system collapse has occurred due to betrayals.
        self.collapse_count = 0
        
        #Dictionary tracking how much each player contributed to system collapses.
        self.collapse_contributions = {str(i): 0 for i in range(n_players)}
        
        #Function used to simulate each turn.
        self.play_turn_func = play_turn_func

    '''
    #Method to select a target player for a given player.
        player: The player who is choosing a target.
    '''
    def choose_target(self, player):
        #If the player's history is empty or 10% random chance, choose a random target.
        if not player.history or random.random() < 0.1:  #10% chance of random target
            return random.choice([i for i in range(self.n_players) if i != player.id])
        else:
            #Otherwise, choose the target with whom this player has had the most interaction (betrayal or cooperation).
            return max(player.history, key=lambda t: sum(player.history[t]))

    '''
    #Method to simulate a round of the game.
        round_num: The current round number in the game.
    '''
    def play_round(self, round_num):
        #Capture the current state of resources.
        state = tuple(self.resources)
        
        #Dictionary to store the actions chosen by each player.
        actions = {}
        
        #Dictionary to store betrayals for each player.
        betrayals = defaultdict(list)

        #Each player chooses a target and decides whether to betray or cooperate.
        for player in self.players:
            target_player = self.choose_target(player)
            action = player.choose_action(state, target_player, round_num)
            actions[str(player.id)] = action
            
            #If the player betrays the target, record the betrayal.
            if action is not None:
                betrayals[action].append(str(player.id))
                
            #Update the player's history after the action is taken.
            player.update_history(str(target_player), action)

        #Simulate the turn and update total points, checking for a system collapse.
        results, self.total_points, _, collapse_occurred = self.play_turn_func(
            actions, self.total_points, self.n_resources
        )

        #Capture the new state after the round.
        new_state = tuple(self.total_points.values())

        #Update each player's Q-table based on the results of the round.
        for player in self.players:
            reward = results[str(player.id)][1]  # Assuming this is the reward for the round.
            player.update_q_table(state, actions[str(player.id)], reward, new_state)

        #If a system collapse occurred, increment the collapse count and record the players involved.
        if collapse_occurred:
            self.collapse_count += 1
            for betrayed, betrayers in betrayals.items():
                if len(betrayers) > 2:
                    for betrayer in betrayers:
                        self.collapse_contributions[betrayer] += 1

        #Return the actions, updated resources, and betrayal details for this round.
        return {
            "actions": actions,
            "resources": self.total_points,
            "betrayals": dict(betrayals),
        }
