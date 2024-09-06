import numpy as np
from collections import defaultdict

def calculate_metrics(game_data):
    metrics = {}
    metrics['overall_cooperation_rate'] = calculate_overall_cooperation_rate(game_data)
    metrics['overall_betrayal_rate'] = calculate_overall_betrayal_rate(game_data)
    cooperation_per_player, betrayal_per_player, resources_per_player = calculate_player_stats(game_data)
    metrics['cooperation_per_player'] = cooperation_per_player
    metrics['betrayal_per_player'] = betrayal_per_player
    metrics['resources_per_player'] = resources_per_player
    best_player, worst_player, best_player_data, worst_player_data = calculate_best_worst_players(
        resources_per_player, cooperation_per_player, betrayal_per_player
    )
    metrics['best_player'] = best_player
    metrics['worst_player'] = worst_player
    metrics['best_player_data'] = best_player_data
    metrics['worst_player_data'] = worst_player_data
    metrics['error_metric'] = calculate_error_metric(resources_per_player)
    metrics['trust_decay_rate'] = calculate_trust_decay_rate(game_data)
    metrics['impact_of_system_collapse'] = calculate_impact_of_system_collapse(game_data)
    metrics['pre_collapse_cooperation'], metrics['post_collapse_cooperation'] = calculate_pre_post_collapse_cooperation(game_data)
    metrics['collaboration_index'] = calculate_collaboration_index(game_data)
    metrics['reciprocity_index'] = calculate_reciprocity_index(game_data)
    
    return metrics

def calculate_overall_cooperation_rate(game_data):
    cooperation_rates = []
    for round_data in game_data:
        actions = round_data['actions']
        cooperation_count = sum(1 for action in actions.values() if action is None)
        cooperation_rate = (cooperation_count / len(actions)) * 100  # Convert to percentage
        cooperation_rates.append(cooperation_rate)
    return cooperation_rates

def calculate_overall_betrayal_rate(game_data):
    betrayal_rates = []
    for round_data in game_data:
        actions = round_data['actions']
        betrayal_count = sum(1 for action in actions.values() if action is not None)
        betrayal_rate = (betrayal_count / len(actions)) * 100  # Convert to percentage
        betrayal_rates.append(betrayal_rate)
    return betrayal_rates

def calculate_player_stats(game_data):
    resources_per_player = defaultdict(int)
    cooperation_per_player = defaultdict(int)
    betrayal_per_player = defaultdict(int)

    for round_data in game_data:
        for player_id, resources in round_data['resources'].items():
            resources_per_player[player_id] = resources  # Use the final resource value
        
        for player_id, action in round_data['actions'].items():
            if action is None:
                cooperation_per_player[player_id] += 1
            else:
                betrayal_per_player[player_id] += 1

    return cooperation_per_player, betrayal_per_player, resources_per_player

def calculate_best_worst_players(resources_per_player, cooperation_per_player, betrayal_per_player):
    best_player_id = max(resources_per_player, key=resources_per_player.get)
    worst_player_id = min(resources_per_player, key=resources_per_player.get)
    
    total_rounds_best = cooperation_per_player[best_player_id] + betrayal_per_player[best_player_id]
    total_rounds_worst = cooperation_per_player[worst_player_id] + betrayal_per_player[worst_player_id]
    
    best_player_data = {
        'resources': resources_per_player[best_player_id],
        'cooperation_rate': (cooperation_per_player[best_player_id] / total_rounds_best) * 100,
        'betrayal_rate': (betrayal_per_player[best_player_id] / total_rounds_best) * 100
    }
    
    worst_player_data = {
        'resources': resources_per_player[worst_player_id],
        'cooperation_rate': (cooperation_per_player[worst_player_id] / total_rounds_worst) * 100,
        'betrayal_rate': (betrayal_per_player[worst_player_id] / total_rounds_worst) * 100
    }

    print(f"Debug: Best Player Data: {best_player_data}")
    print(f"Debug: Worst Player Data: {worst_player_data}")

    return best_player_id, worst_player_id, best_player_data, worst_player_data

def calculate_error_metric(resources_per_player):
    avg_resources = np.mean(list(resources_per_player.values()))
    error_metric = {player_id: resources - avg_resources for player_id, resources in resources_per_player.items()}
    return error_metric

def calculate_trust_decay_rate(game_data):
    trust_decay = defaultdict(list)
    last_betrayal = {}

    for round_num, round_data in enumerate(game_data):
        actions = round_data['actions']
        for player, action in actions.items():
            if action is not None:
                last_betrayal[player] = round_num
            elif player in last_betrayal:
                trust_decay[player].append(round_num - last_betrayal[player])
    
    avg_trust_decay = {player: np.mean(decays) if decays else 0 for player, decays in trust_decay.items()}
    return avg_trust_decay

def calculate_impact_of_system_collapse(game_data):
    collapse_count = 0
    for round_data in game_data:
        betrayals = round_data['betrayals']
        for target, betrayers in betrayals.items():
            if len(betrayers) > 2:
                collapse_count += 1
    
    impact_of_system_collapse = {
        'total_collapses': collapse_count
    }
    return impact_of_system_collapse

def calculate_pre_post_collapse_cooperation(game_data):
    collapse_rounds = []
    cooperation_rates = []

    for round_num, round_data in enumerate(game_data):
        cooperation_count = sum(1 for action in round_data['actions'].values() if action is None)
        cooperation_rate = cooperation_count / len(round_data['actions'])
        cooperation_rates.append(cooperation_rate)

        if any(len(betrayers) > 2 for betrayers in round_data['betrayals'].values()):
            collapse_rounds.append(round_num)

    if collapse_rounds:
        pre_collapse = np.mean(cooperation_rates[:collapse_rounds[0]])
        post_collapse = np.mean(cooperation_rates[collapse_rounds[-1] + 1:])
    else:
        pre_collapse = post_collapse = np.mean(cooperation_rates)

    return pre_collapse * 100, post_collapse * 100

def calculate_collaboration_index(game_data):
    collaboration_index = calculate_overall_cooperation_rate(game_data)  # Example metric
    return collaboration_index

def calculate_reciprocity_index(game_data):
    reciprocal_cooperation = defaultdict(list)
    previous_actions = {}
    
    for round_data in game_data:
        actions = round_data['actions']
        for player, action in actions.items():
            if player in previous_actions:
                if previous_actions[player] is None and action is None:
                    reciprocal_cooperation[player].append(1)
                else:
                    reciprocal_cooperation[player].append(0)
            previous_actions[player] = action
    
    avg_reciprocity = {player: np.mean(coop) if coop else 0 for player, coop in reciprocal_cooperation.items()}
    overall_reciprocity_index = np.mean(list(avg_reciprocity.values()))
    return overall_reciprocity_index * 100