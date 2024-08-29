def play_turn(player_actions, total_points=None, resources=2):
    if total_points == None:
        total_points = {player: 0 for player in player_actions.keys()}
    turn_points = {player: 2 for player in player_actions.keys()}
    lost_players = set()

    # Calculate points for each player
    for player, action in player_actions.items():
        # If player is lost, skip
        if player in lost_players:
            continue

        # If player is betrayed too many times, nullify points and end turn
        times_betrayed = list(player_actions.values()).count(player)
        if times_betrayed > resources:
            turn_points = {player: 0 for player in player_actions.keys()}
            break

        # If cooperates, skip
        if action == None:
            continue

        # If both players betray each other, add to lost players
        if player_actions[action] == player:
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


if __name__ == "__main__":

    actions1 = {"J1": "J2", "J2": "J3", "J3": None, "J4": "J3"}
    results1, total_points1 = play_turn(actions1)
    print(results1)
    print(total_points1)

    actions2 = {"J1": "J2", "J2": "J3", "J3": "J4", "J4": "J3"}
    results2, total_points2 = play_turn(actions2, total_points1)
    print(results2)
    print(total_points2)
