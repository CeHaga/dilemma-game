import numpy as np
import random
from collections import defaultdict, deque

#Player class represents each player in the game
class Player:
    ''' 
id: This is a unique identifier for the player. It distinguishes one player from another in the game.

n_players: This indicates the total number of players in the game. It helps the player know how many opponents they have.

alpha: This is the learning rate, controlling how quickly the player updates their understanding of the game. A higher alpha means the player gives more weight to new experiences, while a lower alpha means the player changes their strategy more slowly.

gamma: This is the discount factor, which balances the importance of immediate rewards versus future rewards. A gamma close to 1 means the player cares a lot about future rewards, while a gamma close to 0 means the player focuses more on immediate rewards.

history_length: This controls how much of the player’s past interactions with other players are remembered. It’s a kind of memory buffer that helps the player track patterns of behavior from other players over time.

betray_probability: This represents the initial likelihood that the player will choose to betray rather than cooperate. It can be adjusted to make a player more or less aggressive in their strategy.
    '''
    def __init__(self, id, n_players, alpha=0.1, gamma=0.9, history_length=10, betray_probability=0.5):
        self.id = id  #ID to identify the player
        self.alpha = alpha  #Learning rate for Q-learning
        self.gamma = gamma  #Discount factor for future rewards
        self.q_table = {}  #Q-table to store state-action values
        self.history = defaultdict(lambda: deque(maxlen=history_length))  #Track interactions with other players
        self.betray_probability = betray_probability  #Initial probability of betrayal
        self.total_resources = 0  #Total resources accumulated by the player

    #Method to get the current state (the resources of all players)
    def get_state(self, resources):
        relative_resources = tuple(res - resources[self.id] for res in resources)
        return relative_resources

    #Method to choose an action (cooperate or betray) based on the state and target player
    def choose_action(self, state, target_player, round_num):
        ''' 
    * random.uniform(0, 1): This function generates a random floating-point number between 0 and 1. This number represents a random chance or "roll of the dice" to decide whether the player will betray or cooperate in this particular situation.

    * Comparison to betray_probability: The generated random number is compared to the player’s betray_probability.
    If the random number is less than the betray_probability, the condition random.uniform(0, 1) < self.betray_probability is True, and the player chooses to betray (return 'betray').
    If the random number is greater than or equal to the betray_probability, the condition is False, and the player chooses to cooperate (return 'cooperate').
        '''
        if random.uniform(0, 1) < self.betray_probability:
            return 'betray'
        else:
            #Default to cooperation if betrayal probability is not triggered
            return 'cooperate'

    #Method to increase the betrayal probability (intensity to win)
    def increase_intensity(self):
        self.betray_probability = min(1.0, self.betray_probability + 0.05)

    #Method to update the history of interactions with another player
    def update_history(self, target_player, action):
        self.history[target_player].append(1 if action == 'betray' else 0)

    #Method to update the Q-table after taking an action
    def update_q_table(self, state, action, reward, new_state):
        #Initialize Q-values if the state is new
        if state not in self.q_table:
            self.q_table[state] = {'cooperate': 0, 'betray': 0}
        if new_state not in self.q_table:
            self.q_table[new_state] = {'cooperate': 0, 'betray': 0}

        #Predict the current Q-value
        q_predict = self.q_table[state][action]
        #Calculate the target Q-value using the reward and the max future reward
        q_target = reward + self.gamma * max(self.q_table[new_state].values())

        #Update the Q-value using the Q-learning formula
        self.q_table[state][action] += self.alpha * (q_target - q_predict)

#Game class represents the overall game logic
class Game:
    def __init__(self, n_players, n_resources, n_rounds, betray_probabilities):
        self.n_players = n_players  #Number of players
        self.n_resources = n_resources  #Initial resources for each player
        self.n_rounds = n_rounds  #Number of rounds to play initially
        #Initialize players with betrayal probabilities
        self.players = [
            Player(i, n_players, betray_probability=betray_probabilities[i]) 
            for i in range(n_players)
        ]
        self.resources = np.full(n_players, n_resources)  #Initialize resources for all players
        self.betrayal_log = []  #Log to track betrayals in each game

    #Method to reset the game for a new round
    def reset(self):
        self.resources = np.full(self.n_players, self.n_resources)  #Reset resources for all players
        self.betrayal_log = []  #Reset betrayal log for a new game

    #Method to check if there is a clear winner
    def has_winner(self):
        max_resources = max(self.resources)
        return list(self.resources).count(max_resources) == 1

    #Method to play one round of the game
    def play_round(self, round_num):
        state = tuple(self.resources)  #Get the current state (resources of all players)
        actions = []
        round_betrayals = []  #Track betrayals in this round
        player_betrayed_counts = defaultdict(int)  #Count how many times each player is betrayed
        
        print(f"Match Round State: {state}")
        for player in self.players:
            #Each player selects another player to target
            target_player = random.choice([i for i in range(self.n_players) if i != player.id])
            #Player chooses an action (cooperate or betray)
            relative_state = player.get_state(self.resources)
            action = player.choose_action(relative_state, target_player, round_num)
            actions.append((player.id, target_player, action))
            #Update history of interactions for the player
            player.update_history(target_player, action)
            #Log the betrayal if it happens
            if action == 'betray':
                round_betrayals.append((player.id, target_player))
                player_betrayed_counts[target_player] += 1
        
        #Handle complex cases of multiple betrayals
        everyone_gets_zero = False
        for player_id, count in player_betrayed_counts.items():
            if count > 2:
                #If a player is betrayed by more than 2 others, all players get 0 resources
                everyone_gets_zero = True
                break

        rewards = np.zeros(self.n_players)  #Initialize rewards for this round

        if not everyone_gets_zero:
            for (player_id, target_player, action) in actions:
                if action == 'betray':
                    if (target_player, player_id, 'betray') in actions:  
                        #Both betray each other
                        rewards[player_id] -= 1
                        rewards[target_player] -= 1
                    else:  
                        #One betrays the other
                        rewards[player_id] += 1
                        rewards[target_player] -= 1
        #If a player was betrayed more than twice, set rewards to zero for everyone
        else:
            rewards.fill(0)
        
        #Update resources and Q-table for each player
        for i, player in enumerate(self.players):
            self.resources[i] += rewards[i]
            player.total_resources += rewards[i]  #Accumulate the player's resources
            new_state = player.get_state(self.resources)
            player.update_q_table(state, actions[i][2], rewards[i], new_state)
        
        #Log the betrayals for this round
        self.betrayal_log.append(round_betrayals)

    #Method to play the initial fixed rounds of the game
    def play_initial_rounds(self):
        for round_num in range(1, self.n_rounds + 1):
            self.play_round(round_num)
    
    #Method to continue the game until a clear winner is found
    def play_until_winner(self):
        round_num = self.n_rounds
        while not self.has_winner():
            round_num += 1
            self.play_round(round_num)
            if not self.has_winner():
                #Increase intensity if no winner
                for player in self.players:
                    player.increase_intensity()

    #Method to play the entire game
    def play_game(self):
        self.play_initial_rounds()
        if not self.has_winner():
            self.play_until_winner()
        #Return total resources after the game
        return [player.total_resources for player in self.players]  

    #Method to display the betrayal log after a game
    def display_betrayal_log(self):
        print("\nBetrayal Log for this Game:")
        for round_index, betrayals in enumerate(self.betrayal_log):
            print(f"  Round {round_index + 1}:")
            if betrayals:
                for betrayer, betrayed in betrayals:
                    print(f"    Player {betrayer} betrayed Player {betrayed}")
            else:
                print("    No betrayals")
        print()

    #Method to display the final results and determine the winner
    def display_final_results(self):
        print("\nFinal Results:")
        total_resources = [(player.id, player.total_resources) for player in self.players]
        sorted_players = sorted(total_resources, key=lambda x: x[1], reverse=True)
        for i, (player_id, resource) in enumerate(sorted_players):
            if i == 0:
                print(f"Winner: Player {player_id} finished with {resource} resources")
            else:
                print(f"Player {player_id} finished with {resource} resources")

if __name__ == "__main__":
    n_players = 4  #Number of players
    n_resources = 2  #Initial resources per player
    n_rounds = 100  #Number of rounds to play initially
    n_games = 1  #Number of games to play for learning

    #Define betrayal probabilities for each player (0 = never betray, 1 = always betray)
    betray_probabilities = [0.0, 0.0, 0.0, 0.0]  #Example values for 4 players

    #Initialize the game
    game = Game(n_players, n_resources, n_rounds, betray_probabilities)  

    #Play the game
    game.play_game()

    #Display the betrayal log
    game.display_betrayal_log()

    #Output final Q-tables, profitability analysis, and interaction histories for each player
    for i, player in enumerate(game.players):
        print(f"Player {i} Final Q-Table:")
        for state, actions in player.q_table.items():
            print(f"  State {state}: {actions}")
        print(f"Player {i} Interaction History with Other Players:")
        for target, history in player.history.items():
            print(f"  With Player {target}: {list(history)}")
        print()

    #Display the final results and winner
    game.display_final_results()
