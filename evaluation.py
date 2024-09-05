from simulation_game import Game

class Evaluation:
    def __init__(self, game_instance, n_rounds):
        self.game_instance = game_instance
        self.n_rounds = n_rounds
        self.betrayals = {player_id: 0 for player_id in range(game_instance.n_players)}
        self.cooperations = {player_id: 0 for player_id in range(game_instance.n_players)}

    def evaluate(self):
        for round_num in range(self.n_rounds):
            # Play a round and get actions
            self.game_instance.play_round(round_num + 1)

            # Track the actions (betrayals or cooperations) taken by players
            actions = {str(player.id): player.history for player in self.game_instance.players}

            betrayals_this_round = set()

            # Log betrayal actions per round
            for player_id, history in actions.items():
                # Check last action in the history
                if history:
                    last_action = history[list(history.keys())[-1]]
                    if last_action[-1] == 1:  # If the last action is a betrayal (1)
                        self.betrayals[int(player_id)] += 1
                        betrayals_this_round.add(int(player_id))

            # Count cooperation as no betrayal from the player in this round
            for player_id in range(self.game_instance.n_players):
                if player_id not in betrayals_this_round:
                    self.cooperations[player_id] += 1

        # Calculate overall cooperation and betrayal rates
        overall_cooperation_rate = (sum(self.cooperations.values()) / (self.n_rounds * self.game_instance.n_players)) * 100
        overall_betrayal_rate = 100 - overall_cooperation_rate

        # Individual cooperation and betrayal rates
        individual_cooperation_rates = {player_id: (self.cooperations[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}
        individual_betrayal_rates = {player_id: (self.betrayals[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}

        # Find the best and worst players based on resources
        final_resources = [player.total_resources for player in self.game_instance.players]
        best_player = final_resources.index(max(final_resources))
        worst_player = final_resources.index(min(final_resources))

        # Betrayal percentage for best and worst players
        betrayal_percentage_best = (self.betrayals[best_player] / self.n_rounds) * 100
        betrayal_percentage_worst = (self.betrayals[worst_player] / self.n_rounds) * 100

        #Custom error metric
        expected_score = 2 * n_rounds #The perfect score is 2 times the number of scores, since the players receive 2 resources per round
        error_metric = {player_id: (expected_score - final_resources[player_id]) / 2 for player_id in range(self.game_instance.n_players)}

        #Display results
        print(f"Best Player: {best_player}")
        print(f"Worst Player: {worst_player}")
        print(f"Betrayal percentage of best player: {betrayal_percentage_best}%")
        print(f"Betrayal percentage of worst player: {betrayal_percentage_worst}%")
        print(f"Error metric: {error_metric}")
        print(f"Overall cooperation rate: {overall_cooperation_rate}%")
        print(f"Overall betrayal rate: {overall_betrayal_rate}%")
        print(f"Individual cooperation rates: {individual_cooperation_rates}")
        print(f"Individual betrayal rates: {individual_betrayal_rates}")

if __name__ == "__main__":
    n_players = 5
    n_resources = 2
    n_rounds = 1000  

    #Initial betrayal probabilities for each player
    betray_probabilities = [0.2, 0.1, 0.5, 0.0, 1.0]

    #Initialize and play the game
    game_instance = Game(n_players, n_resources, betray_probabilities)
    evaluator = Evaluation(game_instance, n_rounds)
    evaluator.evaluate()
