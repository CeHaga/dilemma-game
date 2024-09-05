import random
from collections import defaultdict

def play_turn(player_actions, total_points=None, resources=2):
    """
    Process a single turn of the game. Each player either betrays or cooperates based on their action.
    Handle system collapse logic if a player is betrayed by more than 2 other players.
    
    Args:
    - player_actions: A dictionary of player actions (betrayal or cooperation).
    - total_points: A dictionary of players' current total resources.
    - resources: The default resources given to each player per round.

    Returns:
    - result: The results of the turn, including actions and resources.
    - total_points: Updated total points for each player.
    - betrayals: A dictionary tracking who betrayed whom.
    - collapse_occurred: A boolean indicating if a system collapse happened.
    """
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}
    
    turn_points = {player: resources for player in player_actions.keys()}
    betrayals = defaultdict(list)  #Track who betrayed whom
    collapse_occurred = False  #Track if a collapse occurred

    #Track betrayals
    for player, action in player_actions.items():
        if action is not None:
            betrayals[action].append(player)  #Track which player was betrayed by whom
            print(f"Player {player} betrayed Player {action}")

    #Detect system collapse (if a player is betrayed by more than 2 others)
    for player, betrayers in betrayals.items():
        if len(betrayers) > 2:  #Collapse condition: more than 2 betrayals
            collapse_occurred = True
            print(f"System collapse: Player {player} was betrayed by {len(betrayers)} players.")
            break  #Collapse detected, no need to check further

    #If system collapse occurred, penalize all players by halving their resources and set turn_points to 0
    if collapse_occurred:
        for player in total_points:
            total_points[player] = max(0, total_points[player] // 2)  #Halve everyone's resources
            turn_points[player] = 0  # No one gets the default +2 resources this round
        print("System collapse: All players' resources halved and no points gained this round.")

    #Calculate the points for each player based on betrayals and cooperation
    for player, action in player_actions.items():
        if action is not None:  #Betrayal case
            turn_points[player] += 1  #Gain a point for betraying
            turn_points[action] -= 1  #The betrayed player loses a point

    #Update total points based on turn points
    for player in turn_points:
        total_points[player] += turn_points[player]

    #Return the result, updated total points, betrayals, and whether a collapse occurred
    result = {
        player: (player_actions[player], turn_points[player], total_points[player])
        for player in player_actions.keys()
    }
    
    return result, total_points, betrayals, collapse_occurred
