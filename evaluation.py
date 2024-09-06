import numpy as np
from collections import defaultdict

def calculate_metrics(game_data):
    metrics = {}
    metrics['overall_cooperation_rate'] = calculate_overall_cooperation_rate(game_data)
    metrics['overall_betrayal_rate'] = calculate_overall_betrayal_rate(game_data)
    metrics['cooperation_per_player'] = calculate_cooperation_per_player(game_data)
    metrics['betrayal_per_player'] = calculate_betrayal_per_player(game_data)
    
    best_worst_data = calculate_best_worst_cooperation_betrayal_rates(game_data)
    metrics.update(best_worst_data)
    
    return metrics

def calculate_overall_cooperation_rate(game_data):
    cooperation_rates = []
    for round_data in game_data:
        actions = round_data['actions']
        cooperation_count = sum(1 for action in actions.values() if action is None)
        cooperation_rate = (cooperation_count / len(actions)) * 100
        cooperation_rates.append(cooperation_rate)
    return cooperation_rates

def calculate_overall_betrayal_rate(game_data):
    betrayal_rates = []
    for round_data in game_data:
        actions = round_data['actions']
        betrayal_count = sum(1 for action in actions.values() if action is not None)
        betrayal_rate = (betrayal_count / len(actions)) * 100
        betrayal_rates.append(betrayal_rate)
    return betrayal_rates

def calculate_cooperation_per_player(game_data):
    cooperation_counts = defaultdict(int)
    total_rounds = len(game_data)
    
    for round_data in game_data:
        actions = round_data['actions']
        for player, action in actions.items():
            if action is None:
                cooperation_counts[player] += 1
    
    cooperation_rates = {player: (count / total_rounds) * 100 for player, count in cooperation_counts.items()}
    return cooperation_rates

def calculate_betrayal_per_player(game_data):
    betrayal_counts = defaultdict(int)
    total_rounds = len(game_data)
    
    for round_data in game_data:
        actions = round_data['actions']
        for player, action in actions.items():
            if action is not None:
                betrayal_counts[player] += 1
    
    betrayal_rates = {player: (count / total_rounds) * 100 for player, count in betrayal_counts.items()}
    return betrayal_rates

def calculate_best_worst_cooperation_betrayal_rates(game_data):
    player_resources = defaultdict(int)
    cooperation_counts = defaultdict(int)
    betrayal_counts = defaultdict(int)
    
    total_rounds = len(game_data)
    
    for round_data in game_data:
        actions = round_data['actions']
        resources = round_data['resources']
        for player_id, action in actions.items():
            if action is None:
                cooperation_counts[player_id] += 1
            else:
                betrayal_counts[player_id] += 1
            player_resources[player_id] = resources[player_id]

    # Find the player with the most and least resources
    best_player = max(player_resources, key=player_resources.get)
    worst_player = min(player_resources, key=player_resources.get)
    
    best_cooperation_rate = (cooperation_counts[best_player] / total_rounds) * 100
    worst_cooperation_rate = (cooperation_counts[worst_player] / total_rounds) * 100
    best_betrayal_rate = (betrayal_counts[best_player] / total_rounds) * 100
    worst_betrayal_rate = (betrayal_counts[worst_player] / total_rounds) * 100
    
    return {
        'best_player': best_player,
        'worst_player': worst_player,
        'best_cooperation_rate': best_cooperation_rate,
        'worst_cooperation_rate': worst_cooperation_rate,
        'best_betrayal_rate': best_betrayal_rate,
        'worst_betrayal_rate': worst_betrayal_rate,
        'best_player_resources': player_resources[best_player],
        'worst_player_resources': player_resources[worst_player]
    }
