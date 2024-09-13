#defaultdict: A dictionary that provides a default value for nonexistent keys.
import numpy as np
from collections import defaultdict

'''
#Function to calculate various metrics based on the game data.
    game_data: A list of round data containing actions and resources of players.
'''
def calculate_metrics(game_data):
    #Initialize an empty dictionary to store the calculated metrics.
    metrics = {}

    #Calculate overall cooperation rate across all players and rounds.
    metrics['overall_cooperation_rate'] = calculate_overall_cooperation_rate(game_data)
    
    #Calculate overall betrayal rate across all players and rounds.
    metrics['overall_betrayal_rate'] = calculate_overall_betrayal_rate(game_data)

    #Calculate player-specific statistics (cooperation, betrayal, resources).
    cooperation_per_player, betrayal_per_player, resources_per_player = calculate_player_stats(game_data)
    metrics['cooperation_per_player'] = cooperation_per_player
    metrics['betrayal_per_player'] = betrayal_per_player
    metrics['resources_per_player'] = resources_per_player

    #Identify the best and worst players based on resources and cooperation/betrayal behavior.
    best_player, worst_player, best_player_data, worst_player_data = calculate_best_worst_players(
        resources_per_player, cooperation_per_player, betrayal_per_player
    )
    metrics['best_player'] = best_player
    metrics['worst_player'] = worst_player
    metrics['best_player_data'] = best_player_data
    metrics['worst_player_data'] = worst_player_data

    #Calculate error metric based on deviation from average resources.
    metrics['error_metric'] = calculate_error_metric(resources_per_player)

    #Calculate the rate of trust decay for players after betrayals.
    metrics['trust_decay_rate'] = calculate_trust_decay_rate(game_data)

    #Calculate the impact of system collapses in terms of total collapses.
    metrics['impact_of_system_collapse'] = calculate_impact_of_system_collapse(game_data)

    #Calculate cooperation rates before and after system collapses.
    metrics['pre_collapse_cooperation'], metrics['post_collapse_cooperation'] = calculate_pre_post_collapse_cooperation(game_data)

    #Calculate an index representing collaboration between players.
    metrics['collaboration_index'] = calculate_collaboration_index(game_data)

    #Calculate a reciprocity index to track cooperative behavior reciprocity.
    metrics['reciprocity_index'] = calculate_reciprocity_index(game_data)
    
    #Return the final dictionary of metrics.
    return metrics

'''
#Function to calculate the overall cooperation rate for the game.
    game_data: The list of round data containing actions of all players.
'''
def calculate_overall_cooperation_rate(game_data):
    #Initialize a list to store cooperation rates for each round.
    cooperation_rates = []

    #Loop through each round in the game data.
    for round_data in game_data:
        actions = round_data['actions']

        #Count the number of cooperative actions (None means cooperation).
        cooperation_count = sum(1 for action in actions.values() if action is None)

        #Calculate the cooperation rate as a percentage.
        cooperation_rate = (cooperation_count / len(actions)) * 100
        cooperation_rates.append(cooperation_rate)

    #Return the list of cooperation rates for each round.
    return cooperation_rates

'''
#Function to calculate the overall betrayal rate for the game.
    game_data: The list of round data containing actions of all players.
'''
def calculate_overall_betrayal_rate(game_data):
    #Initialize a list to store betrayal rates for each round.
    betrayal_rates = []

    #Loop through each round in the game data.
    for round_data in game_data:
        actions = round_data['actions']

        #Count the number of betrayal actions (non-None values mean betrayal).
        betrayal_count = sum(1 for action in actions.values() if action is not None)

        #Calculate the betrayal rate as a percentage.
        betrayal_rate = (betrayal_count / len(actions)) * 100
        betrayal_rates.append(betrayal_rate)

    #Return the list of betrayal rates for each round.
    return betrayal_rates

'''
#Function to calculate the player-specific statistics.
    Returns the total cooperation, betrayal, and resources per player.
'''
def calculate_player_stats(game_data):
    #Initialize defaultdicts to store player stats.
    resources_per_player = defaultdict(int)
    cooperation_per_player = defaultdict(int)
    betrayal_per_player = defaultdict(int)

    #Loop through each round in the game data.
    for round_data in game_data:
        #Track each player's resources at the end of the round.
        for player_id, resources in round_data['resources'].items():
            resources_per_player[player_id] = resources

        #Count cooperative and betrayal actions for each player.
        for player_id, action in round_data['actions'].items():
            if action is None:
                cooperation_per_player[player_id] += 1
            else:
                betrayal_per_player[player_id] += 1

    #Return player stats as dictionaries.
    return cooperation_per_player, betrayal_per_player, resources_per_player
'''
#Function to identify the best and worst players based on their performance.
    Returns the player IDs and their respective data.
'''
def calculate_best_worst_players(resources_per_player, cooperation_per_player, betrayal_per_player):
    #Find the player with the maximum and minimum resources.
    best_player_id = max(resources_per_player, key=resources_per_player.get)
    worst_player_id = min(resources_per_player, key=resources_per_player.get)
    
    #Calculate the total number of rounds each player participated in.
    total_rounds_best = cooperation_per_player[best_player_id] + betrayal_per_player[best_player_id]
    total_rounds_worst = cooperation_per_player[worst_player_id] + betrayal_per_player[worst_player_id]
    
    #Create a dictionary to store stats for the best player.
    best_player_data = {
        'resources': resources_per_player[best_player_id],
        'cooperation_rate': (cooperation_per_player[best_player_id] / total_rounds_best) * 100,
        'betrayal_rate': (betrayal_per_player[best_player_id] / total_rounds_best) * 100
    }
    
    #Create a dictionary to store stats for the worst player.
    worst_player_data = {
        'resources': resources_per_player[worst_player_id],
        'cooperation_rate': (cooperation_per_player[worst_player_id] / total_rounds_worst) * 100,
        'betrayal_rate': (betrayal_per_player[worst_player_id] / total_rounds_worst) * 100
    }

    #Debug print statements for best and worst player data.
    print(f"Debug: Best Player Data: {best_player_data}")
    print(f"Debug: Worst Player Data: {worst_player_data}")

    #Return the best and worst player IDs and their respective data.
    return best_player_id, worst_player_id, best_player_data, worst_player_data

'''
#Function to calculate the error metric as the difference between player resources and the average.
    Returns a dictionary of error metrics for each player.
'''
def calculate_error_metric(resources_per_player):
    #Calculate the average resources across all players.
    avg_resources = np.mean(list(resources_per_player.values()))

    #Calculate the difference between each player's resources and the average.
    error_metric = {player_id: resources - avg_resources for player_id, resources in resources_per_player.items()}

    #Return the error metric for each player.
    return error_metric

''''
#Function to calculate the rate at which trust decays after betrayals.
    Returns the average trust decay per player.
'''
def calculate_trust_decay_rate(game_data):
    #Initialize a defaultdict to store trust decay values.
    trust_decay = defaultdict(list)

    #Track the last round in which each player betrayed someone.
    last_betrayal = {}

    #Loop through each round in the game data.
    for round_num, round_data in enumerate(game_data):
        actions = round_data['actions']

        #Update the last betrayal round for players who betrayed in this round.
        for player, action in actions.items():
            if action is not None:
                last_betrayal[player] = round_num
            elif player in last_betrayal:
                trust_decay[player].append(round_num - last_betrayal[player])

    #Calculate the average trust decay for each player.
    avg_trust_decay = {player: np.mean(decays) if decays else 0 for player, decays in trust_decay.items()}

    #Return the average trust decay per player.
    return avg_trust_decay

'''
#Function to calculate the total number of system collapses during the game.
    Returns the total collapse count.
'''
def calculate_impact_of_system_collapse(game_data):
    #Initialize a counter for collapses.
    collapse_count = 0

    #Loop through each round in the game data.
    for round_data in game_data:
        betrayals = round_data['betrayals']

        #Increment collapse count if more than one player betrays the same target.
        for target, betrayers in betrayals.items():
            if len(betrayers) > 1:
                collapse_count += 1

    #Return the total number of collapses.
    impact_of_system_collapse = {
        'total_collapses': collapse_count
    }
    return impact_of_system_collapse

'''
#Function to calculate cooperation rates before and after system collapses.
    Returns the pre-collapse and post-collapse cooperation rates.
'''
def calculate_pre_post_collapse_cooperation(game_data):
    #Initialize lists to store collapse rounds and cooperation rates.
    collapse_rounds = []
    cooperation_rates = []

    #Loop through each round in the game data.
    for round_num, round_data in enumerate(game_data):
        #Calculate the cooperation rate for this round.
        cooperation_count = sum(1 for action in round_data['actions'].values() if action is None)
        cooperation_rate = cooperation_count / len(round_data['actions'])
        cooperation_rates.append(cooperation_rate)

        #Check if a collapse occurred in this round.
        if any(len(betrayers) > 1 for betrayers in round_data['betrayals'].values()):
            collapse_rounds.append(round_num)

    #Calculate the average cooperation rate before and after the first collapse.
    if collapse_rounds:
        pre_collapse = np.mean(cooperation_rates[:collapse_rounds[0]])
        post_collapse = np.mean(cooperation_rates[collapse_rounds[-1] + 1:])
    else:
        pre_collapse = post_collapse = np.mean(cooperation_rates)

    #Return the pre- and post-collapse cooperation rates as percentages.
    return pre_collapse * 100, post_collapse * 100

'''
#Function to calculate a collaboration index for the game.
    Returns the collaboration index.
'''
def calculate_collaboration_index(game_data):
    #Use the overall cooperation rate as an example metric for collaboration.
    collaboration_index = calculate_overall_cooperation_rate(game_data)

    #Return the collaboration index.
    return collaboration_index

'''
#Function to calculate the reciprocity index for the game.
    Returns the overall reciprocity index as a percentage.
'''
def calculate_reciprocity_index(game_data):
    #Initialize a defaultdict to store reciprocal cooperation data.
    reciprocal_cooperation = defaultdict(list)
    
    #Track the actions from previous rounds.
    previous_actions = {}

    #Loop through each round in the game data.
    for round_data in game_data:
        actions = round_data['actions']

        #Compare actions with previous rounds to identify reciprocal cooperation.
        for player, action in actions.items():
            if player in previous_actions:
                if previous_actions[player] is None and action is None:
                    reciprocal_cooperation[player].append(1)
                else:
                    reciprocal_cooperation[player].append(0)
            previous_actions[player] = action

    #Calculate the average reciprocity per player.
    avg_reciprocity = {player: np.mean(coop) if coop else 0 for player, coop in reciprocal_cooperation.items()}

    #Return the overall reciprocity index as a percentage.
    overall_reciprocity_index = np.mean(list(avg_reciprocity.values()))
    return overall_reciprocity_index * 100
