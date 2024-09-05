import matplotlib.pyplot as plt
import numpy as np
import simulation_game  # Assuming this is your simulation script
import os

# Function to run the simulation and plot the graph
def plot_accumulated_resources_graph(n_players, n_resources, n_rounds, betray_probabilities):
    # Initialize the game
    game_instance = simulation_game.Game(n_players, n_resources, betray_probabilities)
    
    # Run the simulation
    resources_over_time = np.zeros((n_rounds, n_players))
    for round_num in range(n_rounds):
        game_instance.play_round(round_num + 1)
        resources_over_time[round_num] = [player.total_resources for player in game_instance.players]

    # Plot the graph
    plt.figure(figsize=(10, 6))
    for player_id in range(n_players):
        # Include betrayal probability in the legend
        plt.plot(range(1, n_rounds + 1), resources_over_time[:, player_id], 
                 label=f'Player {player_id} - ({betray_probabilities[player_id]})')

    # Add labels and title
    plt.xlabel('Rounds')
    plt.ylabel('Accumulated Resources')
    plt.title('Accumulated Resources Over Time for Each Player')
    plt.legend(title='Players - (Betrayal Probability)')

    # Define the full path to save the image in your desired location
    save_path = "/mnt/d/POS_GRADUACAO/MESTRADO/CADEIRAS/CSCW/Artigo Final/script/accumulated_resources_graph.png"
    plt.savefig(save_path)
    print(f"Plot saved at: {save_path}")

    plt.show()

# Parameters
n_players = 5
n_resources = 2
n_rounds = 10000
betray_probabilities = [0.1, 0.5, 0.5, 0.5, 1.0]

# Run the function to create and save the plot
plot_accumulated_resources_graph(n_players, n_resources, n_rounds, betray_probabilities)
