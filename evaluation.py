from simulation_game import Game

class Evaluation:
    def __init__(self, game_instance, n_rounds):
        """Initializes the Evaluation class, sets up game instance, rounds, and tracking for betrayals, cooperation, and collapses."""
        self.game_instance = game_instance
        self.n_rounds = n_rounds
        self.betrayals = {player_id: 0 for player_id in range(game_instance.n_players)}
        self.cooperations = {player_id: 0 for player_id in range(game_instance.n_players)}
        self.collapses = {player_id: 0 for player_id in range(game_instance.n_players)}
        self.collapse_rounds = []
        self.pre_collapse_cooperation = None
        self.post_collapse_cooperation = None
        self.mutual_cooperation = 0
        self.reciprocal_cooperation = {player_id: 0 for player_id in range(game_instance.n_players)}
        self.collaboration_index = 0
        self.cooperation_stability = []
        self.cooperation_streaks = {player_id: 0 for player_id in range(game_instance.n_players)}  # For Cooperation Intensity
        self.influence_on_group = {player_id: 0 for player_id in range(game_instance.n_players)}  # For Influence on Group Behavior
        self.total_betrayals = 0  # To track trust decay rate

    def evaluate(self):
        """Main function to evaluate the game's cooperation, betrayal, and collapse metrics over the rounds."""
        for round_num in range(self.n_rounds):
            # Play a round and get actions
            self.game_instance.play_round(round_num + 1)

            # Track the actions (betrayals or cooperations) taken by players
            actions = {int(player.id): player.history for player in self.game_instance.players}  # Convert player.id to integer

            betrayals_this_round = set()
            player_betrayed_count = {player_id: 0 for player_id in range(self.game_instance.n_players)}

            # Log betrayal actions per round
            for player_id, history in actions.items():
                if history:
                    # Check the last action in the history
                    last_action = history[list(history.keys())[-1]]
                    if last_action[-1] == 1:  # If the last action is a betrayal (1)
                        self.betrayals[player_id] += 1
                        betrayals_this_round.add(player_id)
                        self.total_betrayals += 1

                        # Track who was betrayed
                        betrayed_player = int(list(history.keys())[-1])  # The player they betrayed, converted to integer
                        player_betrayed_count[betrayed_player] += 1
                        self.influence_on_group[player_id] += 1  # Track influence on group behavior

            # Count cooperation as no betrayal from the player in this round
            for player_id in range(self.game_instance.n_players):
                if player_id not in betrayals_this_round:
                    self.cooperations[player_id] += 1
                    self.cooperation_streaks[player_id] += 1  # Track streak of cooperation
                else:
                    self.cooperation_streaks[player_id] = 0  # Reset streak if they betrayed

            # Mutual cooperation: check if all players cooperated in the round
            if len(betrayals_this_round) == 0:
                self.mutual_cooperation += 1

            # Reciprocal cooperation: track if players reciprocate cooperation
            for player_id, history in actions.items():
                if history:
                    previous_player_id = int(list(history.keys())[-1])
                    if player_id not in betrayals_this_round and previous_player_id not in betrayals_this_round:
                        self.reciprocal_cooperation[player_id] += 1

            # Check for collapses in this round (if a player was betrayed more than twice)
            collapse_occurred = False
            for player_id, betray_count in player_betrayed_count.items():
                if betray_count > 2:  # Collapse if a player is betrayed more than twice
                    self.collapses[player_id] += 1
                    collapse_occurred = True
                    self.collapse_rounds.append(round_num)

            # Measure pre-collapse cooperation rate
            if collapse_occurred and not self.pre_collapse_cooperation:
                self.pre_collapse_cooperation = self.calculate_cooperation_rate(0, round_num)

        # If no collapses occurred, treat the entire game as pre-collapse behavior
        if not self.pre_collapse_cooperation:
            self.pre_collapse_cooperation = self.calculate_cooperation_rate(0, self.n_rounds)

        # If collapses occurred, measure post-collapse cooperation rate
        if self.collapse_rounds:
            last_collapse_round = self.collapse_rounds[-1]
            self.post_collapse_cooperation = self.calculate_cooperation_rate(last_collapse_round, self.n_rounds)
        else:
            # If no collapses occurred, the post-collapse rate equals the overall cooperation rate
            self.post_collapse_cooperation = self.pre_collapse_cooperation

        # Calculate overall cooperation and betrayal rates
        overall_cooperation_rate = (sum(self.cooperations.values()) / (self.n_rounds * self.game_instance.n_players)) * 100
        overall_betrayal_rate = 100 - overall_cooperation_rate

        # Individual cooperation rates
        individual_cooperation_rates = {player_id: (self.cooperations[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}
        
        # Individual betrayal rates
        individual_betrayal_rates = {player_id: (self.betrayals[player_id] / self.n_rounds) * 100 for player_id in range(self.game_instance.n_players)}

        # Find the best and worst players based on resources
        final_resources = [player.total_resources for player in self.game_instance.players]
        best_player = final_resources.index(max(final_resources))
        worst_player = final_resources.index(min(final_resources))

        # Betrayal percentage for best and worst players
        betrayal_percentage_best = (self.betrayals[best_player] / self.n_rounds) * 100
        betrayal_percentage_worst = (self.betrayals[worst_player] / self.n_rounds) * 100

        # Custom error metric
        expected_score = 2 * self.n_rounds  # The perfect score is 2 times the number of rounds
        error_metric = {player_id: (expected_score - final_resources[player_id]) / 2 for player_id in range(self.game_instance.n_players)}

        # Calculate collaboration index
        self.collaboration_index = self.calculate_collaboration_index()

        # Calculate cooperation intensity (continuous streaks of cooperation)
        cooperation_intensity = sum(self.cooperation_streaks.values()) / self.n_rounds

        # Calculate reciprocity index
        reciprocity_index = sum(self.reciprocal_cooperation.values()) / (self.n_rounds * self.game_instance.n_players)

        # Calculate influence on group behavior
        influence_index = sum(self.influence_on_group.values()) / (self.n_rounds * self.game_instance.n_players)

        # Trust decay rate: total betrayals / total interactions
        trust_decay_rate = self.total_betrayals / (self.n_rounds * self.game_instance.n_players)

        # Display results
        self.display_results(best_player, worst_player, betrayal_percentage_best, betrayal_percentage_worst, overall_cooperation_rate, 
                             overall_betrayal_rate, individual_cooperation_rates, individual_betrayal_rates, error_metric, self.collapses, 
                             cooperation_intensity, reciprocity_index, influence_index, trust_decay_rate)

    def calculate_cooperation_rate(self, start_round, end_round):
        """Calculates the cooperation rate between the given rounds (start_round to end_round)."""
        total_cooperation = 0
        for player_id in range(self.game_instance.n_players):
            total_cooperation += self.cooperations[player_id]
        return (total_cooperation / ((end_round - start_round) * self.game_instance.n_players)) * 100

    def calculate_collaboration_index(self):
        """Calculates the collaboration index based on direct and indirect cooperation."""
        total_cooperations = sum(self.cooperations.values())
        total_interactions = self.n_rounds * self.game_instance.n_players
        return (total_cooperations / total_interactions) * 100

    def display_results(self, best_player, worst_player, betrayal_percentage_best, betrayal_percentage_worst, 
                        overall_cooperation_rate, overall_betrayal_rate, individual_cooperation_rates, 
                        individual_betrayal_rates, error_metric, collapses, 
                        cooperation_intensity, reciprocity_index, influence_index, trust_decay_rate):
        """Display the calculated metrics."""
        print(f"Best Player: {best_player}")
        print(f"Worst Player: {worst_player}")
        print(f"Betrayal percentage of best player: {betrayal_percentage_best}%")
        print(f"Betrayal percentage of worst player: {betrayal_percentage_worst}%")
        print(f"Error metric: {error_metric}")
        print(f"Overall cooperation rate: {overall_cooperation_rate}%")
        print(f"Overall betrayal rate: {overall_betrayal_rate}%")
        print(f"Individual cooperation rates: {individual_cooperation_rates}")
        print(f"Individual betrayal rates: {individual_betrayal_rates}")
        print(f"Total collapses: {sum(collapses.values())}")
        print(f"Pre-collapse cooperation rate: {self.pre_collapse_cooperation}%")
        print(f"Post-collapse cooperation rate: {self.post_collapse_cooperation}%")
        print(f"Collaboration Index: {self.collaboration_index}%")
        print(f"Cooperation Intensity: {cooperation_intensity}")
        print(f"Reciprocity Index: {reciprocity_index}")
        print(f"Influence on Group Behavior: {influence_index}")
        print(f"Trust Decay Rate: {trust_decay_rate}")

if __name__ == "__main__":
    n_players = 5
    n_resources = 2
    n_rounds = 1000  

    # Initial betrayal probabilities for each player
    betray_probabilities = [0.2, 0.1, 0.5, 0.0, 1.0]

    # Initialize and play the game
    game_instance = Game(n_players, n_resources, betray_probabilities)
    evaluator = Evaluation(game_instance, n_rounds)
    evaluator.evaluate()
