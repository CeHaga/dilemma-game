import random
from collections import defaultdict


def play_turn(player_actions, total_points=None, resources=2):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)
    collapse_occurred = False

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            break

    if collapse_occurred:
        for player in total_points:
            total_points[player] = max(0, total_points[player] // 2)
            turn_points[player] = 0
    else:
        for player, action in player_actions.items():
            if action is not None:
                turn_points[player] += 1
                turn_points[action] -= 1

    for player in turn_points:
        total_points[player] += turn_points[player]

    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }

    return result, total_points, betrayals, collapse_occurred


def play_turn_sim2(player_actions, total_points=None, resources=2):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)
    collapse_occurred = False
    involved_players = set()

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            involved_players.add(player)
            involved_players.update(betrayers)
            break

    for player, action in player_actions.items():
        if player in involved_players:
            turn_points[player] = 0
            continue

        if action is None:
            continue

        turn_points[player] += 1
        if action not in involved_players:
            turn_points[action] -= 1

    for player in turn_points:
        total_points[player] += turn_points[player]

    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }

    return result, total_points, betrayals, collapse_occurred


def play_turn_sim3(player_actions, total_points=None, resources=2):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)
    collapse_occurred = False
    involved_players = set()

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            involved_players.add(player)
            involved_players.update(betrayers)
            break

    for player, action in player_actions.items():
        if player in involved_players:
            turn_points[player] = 0
            total_points[player] = max(0, total_points[player] // 2)
            continue

        if action is None:
            continue

        turn_points[player] += 1
        if action not in involved_players:
            turn_points[action] -= 1

    for player in turn_points:
        total_points[player] += turn_points[player]

    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }

    return result, total_points, betrayals, collapse_occurred


def play_turn_sim4(player_actions, total_points=None, resources=2):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)
    collapse_occurred = False
    betrayed_player = None

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            betrayed_player = player
            break

    for player, action in player_actions.items():
        if player == betrayed_player:
            turn_points[player] = resources * len(betrayals[betrayed_player])
            continue

        if player in betrayals[betrayed_player]:
            turn_points[player] = 0
            continue

        if action is None:
            continue

        turn_points[player] += 1
        if action not in betrayals[betrayed_player]:
            turn_points[action] -= 1

    for player in turn_points:
        total_points[player] += turn_points[player]

    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }

    return result, total_points, betrayals, collapse_occurred
