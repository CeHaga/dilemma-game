#random: Used for random number generation.
#defaultdict: A dictionary subclass that provides a default value for non-existent keys.
import random
from collections import defaultdict

'''
#Function to handle a single turn of the game.
player_actions: A dictionary representing the actions of each player.
total_points: A dictionary of total points per player, initialized to zero if not provided.
resources: The resources available for each player at the beginning of the turn.
'''
def play_turn(player_actions, total_points=None, resources=2):
    #Initialize total points if not provided.
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    #Set initial turn points based on available resources for each player.
    turn_points = {player: resources for player in player_actions.keys()}
    
    #Create a defaultdict to track which players are betrayed.
    betrayals = defaultdict(list)
    
    #A flag to check if a collapse occurred (when more than two betrayals happen).
    collapse_occurred = False

    #Iterate over each player's action to check for betrayals.
    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    #If any player is betrayed by more than two others, a collapse occurs.
    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            break

    #If a collapse occurred, halve each player's total points and reset turn points.
    if collapse_occurred:
        for player in total_points:
            total_points[player] = max(0, total_points[player] // 2)
            turn_points[player] = 0
    else:
        #If no collapse, adjust points based on betrayals and cooperation.
        for player, action in player_actions.items():
            if action is not None:
                turn_points[player] += 1
                turn_points[action] -= 1

    #Update total points after the turn.
    for player in turn_points:
        total_points[player] += turn_points[player]

    #Create a result dictionary showing the action, points gained in the turn, and total points for each player.
    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }

    #Return the result, updated total points, betrayals, and collapse flag.
    return result, total_points, betrayals, collapse_occurred

#Similar to the play_turn function but includes a set of involved players in case of a collapse.
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

    #Track players involved in the collapse.
    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            involved_players.add(player)
            involved_players.update(betrayers)
            break

    #If collapse occurs, all involved players lose their turn points.
    for player, action in player_actions.items():
        if player in involved_players:
            turn_points[player] = 0
            continue

        if action is None:
            continue

        #Adjust points for players not involved in the collapse.
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

#Another simulation where involved players' total points are halved during a collapse.
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

#A simulation where the betrayed player gains points based on the number of betrayers.
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

#A global dictionary to keep track of the number of times each player betrays.
times_betrayers = {}

#Simulation that includes tracking betrayer history and a multiplier effect on their resources.
def play_turn_sim5(player_actions, total_points=None, resources=10, multiplier=5):
    global times_betrayers

    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {
        player: max(resources - times_betrayers.get(player, 0) * multiplier, 0)
        for player in player_actions.keys()
    }
    betrayals = defaultdict(list)
    collapse_occurred = False
    betrayed_player = None

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:
            collapse_occurred = True
            for betrayer in betrayers:
                times_betrayers[betrayer] = times_betrayers.get(betrayer, 0) + 1
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

''' 
This scenario represents the "Tragedy of the Commons," where, in the event of a collapse, all players lose the resources accumulated during that turn, and no one gains anything.
'''
def play_turn_v2(player_actions, total_points=None, resources=1):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}

    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)
    collapse_occurred = False

    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)

    for player, betrayers in betrayals.items():
        if len(betrayers) > resources:
            collapse_occurred = True
            break

    if collapse_occurred:
        for player in total_points:
            total_points[player] = 0# max(0, total_points[player] // 2)
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

''' 
In this scenario, in the event of a collapse, only the players who betrayed lose all their resources in that turn and must start from scratch. The other players, not involved in the betrayal, remain unaffected
'''
def play_turn_sim2_v2(player_actions, total_points=None, resources=1):
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
        if len(betrayers) > resources:
            collapse_occurred = True
            involved_players.update(betrayers)

    for player, action in player_actions.items():
        if player in involved_players:
            turn_points[player] = 0
            total_points[player] = 0# max(0, total_points[player] // 2)
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
