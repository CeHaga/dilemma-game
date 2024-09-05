from simulation_game import Game

#Define the Evaluation class to handle game evaluations
class Evaluation:
    #Constructor for the Evaluation class
    #Initializes the Evaluation object with the game instance and number of rounds
    def __init__(self, game_instance, n_rounds):
        #Save the game instance object that will be evaluated
        self.game_instance = game_instance
        
        #Save the number of rounds for the evaluation process
        self.n_rounds = n_rounds

        #Initialize a dictionary to track the number of betrayals for each player, starting at 0
        self.betrayals = {player_id: 0 for player_id in range(game_instance.n_players)}

        #Initialize a dictionary to track the number of cooperations for each player, starting at 0
        self.cooperations = {player_id: 0 for player_id in range(game_instance.n_players)}

    #Main evaluation function that runs through the simulation and computes various metrics
    def evaluate(self):
        #Loop through each round of the game
        for round_num in range(self.n_rounds):
            #Play a round in the game, where players make decisions (cooperate/betray)
            self.game_instance.play_round(round_num + 1)

            #Collect the actions taken by players during the round
            #'actions' stores each player's interaction history (who they betrayed/cooperated with)
            actions = {str(player.id): player.history for player in self.game_instance.players}

            #A set to track players who betrayed in the current round
            betrayals_this_round = set()

            #Loop through each player's actions to log betrayals
            for player_id, history in actions.items():
                #Check if the player has a history (i.e., actions taken in the game)
                if history:
                    #Get the last action of the player to determine their most recent behavior
                    last_action = history[list(history.keys())[-1]]
                    
                    #If the last action was a betrayal (encoded as 1), log the betrayal
                    if last_action[-1] == 1:
                        #Increment the betrayal count for the player
                        self.betrayals[int(player_id)] += 1
                        
                        #Add the player to the set of players who betrayed in this round
                        betrayals_this_round.add(int(player_id))

            #Loop through all players to log cooperation (i.e., no betrayal during the round)
            for player_id in range(self.game_instance.n_players):
                #If a player did not betray in this round, count it as cooperation
                if player_id not in betrayals_this_round:
                    self.cooperations[player_id] += 1

        #Calculate the overall cooperation rate
        #This is the total number of cooperative actions divided by the total possible actions, multiplied by 100
        overall_cooperation_rate = (sum(self.cooperations.values()) / (self.n_rounds * self.game_instance.n_players)) * 100

        # Calculate the overall betrayal rate as the complement of the cooperation rate
        overall_betrayal_rate = 100 - overall_cooperation_rate

        #Calculate individual cooperation rates for each player
        #This is the number of cooperative actions by each player divided by the number of rounds, multiplied by 100
        individual_cooperation_rates = {player_id: (self.cooperations[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}
        
        #Calculate individual betrayal rates for each player
        #This is the number of betrayals by each player divided by the number of rounds, multiplied by 100
        individual_betrayal_rates = {player_id: (self.betrayals[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}

        #Get the final resource totals for each player at the end of the game
        final_resources = [player.total_resources for player in self.game_instance.players]

        #Identify the best player (player with the highest resources)
        best_player = final_resources.index(max(final_resources))

        #Identify the worst player (player with the lowest resources)
        worst_player = final_resources.index(min(final_resources))

        #Calculate the betrayal percentage for the best player
        #This is the number of betrayals by the best player divided by the number of rounds, multiplied by 100
        betrayal_percentage_best = (self.betrayals[best_player] / self.n_rounds) * 100

        #Calculate the betrayal percentage for the worst player
        #This is the number of betrayals by the worst player divided by the number of rounds, multiplied by 100
        betrayal_percentage_worst = (self.betrayals[worst_player] / self.n_rounds) * 100

        #Calculate the expected score assuming everyone cooperated for all rounds
        #Players would receive 2 resources per round, so the expected score is 2 times the number of rounds
        expected_score = 2 * self.n_rounds

        #Calculate a custom error metric for each player
        #This metric is the difference between the expected score and the player's actual score, divided by 2
        error_metric = {player_id: (expected_score - final_resources[player_id]) / 2 for player_id in range(self.game_instance.n_players)}

        #Print the results of the evaluation
        print(f"Best Player: {best_player}")
        print(f"Worst Player: {worst_player}")
        print(f"Betrayal percentage of best player: {betrayal_percentage_best}%")
        print(f"Betrayal percentage of worst player: {betrayal_percentage_worst}%")
        print(f"Error metric: {error_metric}")
        print(f"Overall cooperation rate: {overall_cooperation_rate}%")
        print(f"Overall betrayal rate: {overall_betrayal_rate}%")
        print(f"Individual cooperation rates: {individual_cooperation_rates}")
        print(f"Individual betrayal rates: {individual_betrayal_rates}")

#Main execution block of the program
if __name__ == "__main__":
    #Set the number of players in the game
    n_players = 5
    
    #Set the initial resources for each player
    n_resources = 2
    
    #Set the number of rounds to be played in the game
    n_rounds = 1000  

    #Set the initial betrayal probabilities for each player
    betray_probabilities = [0.2, 0.1, 0.5, 0.0, 1.0]

    #Initialize a new game instance with the given number of players, resources, and betrayal probabilities
    game_instance = Game(n_players, n_resources, betray_probabilities)

    #Create an instance of the Evaluation class with the game instance and number of rounds
    evaluator = Evaluation(game_instance, n_rounds)

    #Run the evaluation and display the results
    evaluator.evaluate()
