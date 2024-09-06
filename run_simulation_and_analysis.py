import numpy as np
from simulation_game import Game
from evaluation import calculate_metrics
from graphic_generation import generate_plots

def run_simulation_and_analysis(n_players, n_resources, n_rounds, betray_probabilities):
    # Run simulation
    game_instance = Game(n_players, n_resources, betray_probabilities)
    game_data = []
    
    for round_num in range(1, n_rounds + 1):
        round_result = game_instance.play_round(round_num)
        game_data.append({
            'round_num': round_num,
            'actions': round_result['actions'],
            'resources': round_result['resources'],
            'betrayals': round_result['betrayals']
        })
    
    # Calculate metrics
    metrics = calculate_metrics(game_data)
    
    # Generate plots
    plots = generate_plots(metrics, n_rounds)
    
    return game_data, metrics, plots

if __name__ == "__main__":
    # Set simulation parameters
    n_players = 5
    n_resources = 2
    n_rounds = 10000
    betray_probabilities = [0.1, 0.0, 0.2, 0.5, 1.0]
    
    # Run simulation and analysis
    game_data, metrics, plots = run_simulation_and_analysis(n_players, n_resources, n_rounds, betray_probabilities)
    
    # Save plots
    for name, fig in plots.items():
        fig.savefig(f'{name}_plot.png', dpi=300, bbox_inches='tight')
    
    # Print some summary statistics
    print(f"Simulation completed for {n_rounds} rounds with {n_players} players.")
    print(f"Average cooperation rate: {np.mean(metrics['overall_cooperation_rate']):.2f}%")
    print(f"Number of system collapses: {len(metrics['impact_of_system_collapse']) if 'impact_of_system_collapse' in metrics else 0}")
