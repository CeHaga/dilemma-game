import random
from collections import defaultdict

def play_turn(player_actions, total_points=None, resources=2):
    if total_points is None:
        total_points = {player: 0 for player in player_actions.keys()}
    turn_points = {player: 2 for player in player_actions.keys()}
    lost_players = set()
    betrayals = defaultdict(int)  # Track how many times each player is betrayed

    # Track betrayals
    for player, action in player_actions.items():
        if action is not None:
            betrayals[action] += 1  # Track how many times each player is betrayed

    # Check for random event due to repeated betrayal
    for player, times_betrayed in betrayals.items():
        if times_betrayed > 2:
            # Random event: Choose one player involved in the betrayal
            involved_players = [player] + [p for p, a in player_actions.items() if a == player]
            chosen_player = random.choice(involved_players)

            # Randomly apply one of the two effects
            if random.choice([True, False]):
                # Effect 1: Chosen player loses half of all accumulated resources
                total_points[chosen_player] = max(0, total_points[chosen_player] // 2)
                print(f"Player {chosen_player} loses half of their accumulated resources!")
            else:
                # Effect 2: Chosen player gains all the resources the others involved would have gained
                gained_resources = sum(turn_points[p] for p in involved_players) #if p != chosen_player)
                total_points[chosen_player] += gained_resources
                for p in involved_players:
                    if p != chosen_player:
                        turn_points[p] = 0  # Others get nothing
                print(f"Player {chosen_player} gains {gained_resources} resources from others!")
            
            # No need to process further after the random event is triggered
            break

    # Continue with the standard point calculation if no random event
    for player, action in player_actions.items():
        # If player is lost, skip
        if player in lost_players:
            continue

        # If cooperates, skip
        if action is None:
            continue

        # If both players betray each other, add to lost players
        if player_actions.get(action) == player:
            lost_players.add(player)
            lost_players.add(action)
            continue

        # If player betrays and other doesn't, steal point
        turn_points[player] += 1
        turn_points[action] -= 1

    # Remove points from lost players
    for player in lost_players:
        turn_points[player] = -1

    # Add points to total points
    total_points = {
        player: total_points[player] + turn_points[player]
        for player in player_actions.keys()
    }

    result = {
        player: (action, turn_points[player], total_points[player])
        for player, action in player_actions.items()
    }

    return result, total_points

