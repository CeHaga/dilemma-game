from random import randint
import sys, getopt


def main(players, resources, total_turns, debug):
    total_points = [0] * players

    # For each turn
    for turn in range(total_turns):
        turn_points = [resources] * players
        lost_players = set()
        betrayed_players = [-1] * players

        # Each player decides to betray or cooperate
        for player in range(players):
            betray_player = randint(-1, players - 1)
            if betray_player == player:
                betray_player = -1
            betrayed_players[player] = betray_player
            if betray_player == -1:
                if debug:
                    print(f"Player {player} cooperates")
                continue
            if debug:
                print(f"Player {player} betrays {betray_player}")

        # Calculate points for each player
        for player in range(players):
            # If player is lost, skip
            if player in lost_players:
                continue

            # If player is betrayed too many times, nullify points and end turn
            times_betrayed = betrayed_players.count(player)
            if times_betrayed > resources:
                turn_points = [0] * players
                if debug:
                    print(f"Player {player} betrayed too many times")
                break
            betray = betrayed_players[player]

            # If cooperates, skip
            if betray == -1:
                continue

            # If both players betray each other, add to lost players
            if betrayed_players[betray] == player:
                if debug:
                    print(f"Player {player} and {betray} betrayed each other")
                lost_players.add(player)
                lost_players.add(betray)
                continue

            # If player betrays and other doesn't, steal point
            turn_points[player] += 1
            turn_points[betray] -= 1

        # Remove points from lost players
        for player in lost_players:
            turn_points[player] = -1

        total_points = [total_points[i] + turn_points[i] for i in range(players)]
        if debug:
            input(f"Turn {turn + 1}: {turn_points} -> {total_points}")
    if debug:
        print(f"Total points: {total_points}")
        print(f"Winner: {total_points.index(max(total_points))}")
    return total_points


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "p:r:t:d", ["players=", "resources=", "turns=", "debug"]
        )
    except getopt.GetoptError:
        print("game.py [-p <players>] [-r <resources>] [-t <turns>] [-d]")
        sys.exit(2)

    players = 4
    resources = 2
    total_turns = 20
    debug = False
    for opt, arg in opts:
        if opt in ("-p", "--players"):
            players = int(arg)
        elif opt in ("-r", "--resources"):
            resources = int(arg)
        elif opt in ("-t", "--turns"):
            total_turns = int(arg)
        elif opt in ("-d", "--debug"):
            debug = True

    result = main(players, resources, total_turns, debug)
    print(result)
