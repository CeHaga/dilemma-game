from random import randint
import sys, getopt


def main(players, resources, total_turns):
    total_points = [0] * players
    for turn in range(total_turns):
        turn_points = [resources] * players
        lost_players = set()
        betrayed_players = [-1] * players
        for player in range(players):
            betray_player = randint(-1, players - 1)
            if betray_player == player:
                betray_player = -1
            betrayed_players[player] = betray_player
            if betray_player == -1:
                print(f"Player {player} cooperates")
                continue
            print(f"Player {player} betrays {betray_player}")
        for player in range(players):
            if player in lost_players:
                continue
            times_betrayed = betrayed_players.count(player)
            if times_betrayed > resources:
                turn_points = [0] * players
                print(f"Player {player} betrayed too many times")
                break
            betray = betrayed_players[player]
            if betray == -1:
                continue
            if betrayed_players[betray] == player:
                print(f"Player {player} and {betray} betrayed each other")
                lost_players.add(player)
                lost_players.add(betray)
                continue
            turn_points[player] += 1
            turn_points[betray] -= 1
        for player in lost_players:
            turn_points[player] = -1
        total_points = [total_points[i] + turn_points[i] for i in range(players)]
        input(f"Turn {turn + 1}: {turn_points}")
    print(f"Total points: {total_points}")


if __name__ == "__main__":
    # Get args from command line
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "p:r:t:", ["players=", "resources=", "turns="]
        )
    except getopt.GetoptError:
        print("game.py -p <players> -r <resources> -t <turns>")
        sys.exit(2)

    players = 4
    resources = 2
    total_turns = 20
    for opt, arg in opts:
        if opt in ("-p", "--players"):
            players = int(arg)
        elif opt in ("-r", "--resources"):
            resources = int(arg)
        elif opt in ("-t", "--turns"):
            total_turns = int(arg)

    main(players, resources, total_turns)
