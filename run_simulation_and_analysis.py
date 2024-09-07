import numpy as np
from simulation_game import Game
from game2 import play_turn_v2, play_turn_sim2_v2
from evaluation import calculate_metrics
from graphic_generation import generate_plots
import matplotlib.pyplot as plt
import os


def run_simulation_and_analysis(
    n_players, n_resources, n_rounds, betray_probabilities, simulation_type
):
    # Choose the appropriate play_turn function based on simulation_type
    if simulation_type == 1:
        play_turn_func = play_turn_v2
    elif simulation_type == 2:
        play_turn_func = play_turn_sim2_v2

    # Run simulation
    game_instance = Game(n_players, n_resources, betray_probabilities, play_turn_func)
    game_data = []
    resources_over_time = {str(i): [] for i in range(n_players)}

    for round_num in range(1, n_rounds + 1):
        round_result = game_instance.play_round(round_num)
        game_data.append(
            {
                "round_num": round_num,
                "actions": round_result["actions"],
                "resources": round_result["resources"],
                "betrayals": round_result["betrayals"],
            }
        )

        # Collect resources for each player at every round
        for player_id, resources in round_result["resources"].items():
            resources_over_time[player_id].append(resources)

    # Calculate metrics
    metrics = calculate_metrics(game_data)
    metrics["resources_over_time"] = resources_over_time

    # Debug print statements
    print("Debug: Metrics after calculation:")
    print(f"Best player: {metrics['best_player']}")
    print(f"Worst player: {metrics['worst_player']}")
    print(f"Best player data: {metrics['best_player_data']}")
    print(f"Worst player data: {metrics['worst_player_data']}")

    # Generate plots
    plots = generate_plots(metrics, n_rounds)

    # Add resources_over_time to the returned values
    return game_data, metrics, plots


if __name__ == "__main__":
    # Set simulation parameters
    n_players = 5
    n_resources = 2
    n_rounds = 100
    betray_probabilities = [0, 0.5, 1, 5, 10]

    scenarios = [1, 2]

    # Define the path where images will be saved
    image_path = "images"

    # Create the directory if it doesn't exist
    os.makedirs(image_path, exist_ok=True)

    for scenario in scenarios:
        # Run simulation and analysis
        game_data, metrics, plots = run_simulation_and_analysis(
            n_players, n_resources, n_rounds, betray_probabilities, scenario
        )

        scenario_path = os.path.join(image_path, f"scenario_{scenario}")

        os.makedirs(scenario_path, exist_ok=True)

        # Save plots
        for name, fig in plots.items():
            fig.savefig(
                os.path.join(scenario_path, f"{name}_plot.png"),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close(fig)  # Close the figure to free up memory

        print(f"\nPlots have been saved in: {scenario_path}")

        # Print some summary statistics
        print(f"\nSimulation completed for {n_rounds} rounds with {n_players} players.")
        print(
            f"Average cooperation rate: {np.mean(metrics['overall_cooperation_rate']):.2f}%"
        )
        print(
            f"Number of system collapses: {metrics['impact_of_system_collapse']['total_collapses']}"
        )
        print(f"\nBest Player (ID {metrics['best_player']}):")
        print(f"  Total Resources: {metrics['best_player_data']['resources']}")
        print(
            f"  Cooperation Rate: {metrics['best_player_data']['cooperation_rate']:.2f}%"
        )
        print(f"  Betrayal Rate: {metrics['best_player_data']['betrayal_rate']:.2f}%")
        print(f"\nWorst Player (ID {metrics['worst_player']}):")
        print(f"  Total Resources: {metrics['worst_player_data']['resources']}")
        print(
            f"  Cooperation Rate: {metrics['worst_player_data']['cooperation_rate']:.2f}%"
        )
        print(f"  Betrayal Rate: {metrics['worst_player_data']['betrayal_rate']:.2f}%")

        print("\nPlots have been saved as PNG files.")
