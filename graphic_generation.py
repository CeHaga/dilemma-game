import matplotlib.pyplot as plt
import numpy as np

plt.style.use('classic')

def generate_plots(metrics, n_rounds):
    plots = {}
    
    plots['overall_cooperation'] = plot_overall_cooperation(metrics['overall_cooperation_rate'], n_rounds)
    plots['overall_betrayal'] = plot_overall_betrayal(metrics['overall_betrayal_rate'], n_rounds)
    plots['cooperation_betrayal_per_player'] = plot_cooperation_betrayal_per_player(metrics['cooperation_per_player'], metrics['betrayal_per_player'])
    plots['best_vs_worst'] = plot_best_vs_worst_comparison(
        metrics['best_player'],
        metrics['worst_player'],
        metrics['best_player_data'],
        metrics['worst_player_data']
    )
    plots['trust_decay'] = plot_trust_decay_rate(metrics['trust_decay_rate'])
    plots['collapse_impact'] = plot_pre_post_collapse_cooperation(metrics['pre_collapse_cooperation'], metrics['post_collapse_cooperation'])
    
    return plots

def plot_overall_cooperation(cooperation_rates, n_rounds):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(1, n_rounds + 1), cooperation_rates, color='#1f77b4', linewidth=2)
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Cooperation Rate (%)', fontsize=12)
    ax.set_title('Overall Cooperation Rate Over Time', fontsize=14, fontweight='bold')
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    return fig

def plot_overall_betrayal(betrayal_rates, n_rounds):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(1, n_rounds + 1), betrayal_rates, color='red', linewidth=2)
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Betrayal Rate (%)', fontsize=12)
    ax.set_title('Overall Betrayal Rate Over Time', fontsize=14, fontweight='bold')
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    return fig

def plot_cooperation_betrayal_per_player(cooperation_rates, betrayal_rates):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    players = list(cooperation_rates.keys())
    cooperation_values = [cooperation_rates[player] for player in players]
    betrayal_values = [betrayal_rates[player] for player in players]
    
    # Cooperation Rate plot
    ax[0].bar(players, cooperation_values, color='green', label='Cooperation Rate')
    for i, v in enumerate(cooperation_values):
        ax[0].text(i, v + 1, f'{v}', ha='center')
    ax[0].set_xlabel('Players')
    ax[0].set_ylabel('Count')
    ax[0].set_title('Cooperation Count Per Player')
    ax[0].set_ylim(0, max(cooperation_values) * 1.1)
    
    # Betrayal Rate plot
    ax[1].bar(players, betrayal_values, color='red', label='Betrayal Rate')
    for i, v in enumerate(betrayal_values):
        ax[1].text(i, v + 1, f'{v}', ha='center')
    ax[1].set_xlabel('Players')
    ax[1].set_ylabel('Count')
    ax[1].set_title('Betrayal Count Per Player')
    ax[1].set_ylim(0, max(betrayal_values) * 1.1)
    
    plt.tight_layout()
    plt.show()
    return fig

def plot_best_vs_worst_comparison(best_player, worst_player, best_player_data, worst_player_data):
    print("Debug: Entering plot_best_vs_worst_comparison")
    print(f"Debug: Best player: {best_player}, Worst player: {worst_player}")
    print(f"Debug: Best player data: {best_player_data}")
    print(f"Debug: Worst player data: {worst_player_data}")

    resources = [best_player_data['resources'], worst_player_data['resources']]
    cooperation_rate = [best_player_data['cooperation_rate'], worst_player_data['cooperation_rate']]
    betrayal_rate = [best_player_data['betrayal_rate'], worst_player_data['betrayal_rate']]

    print(f"Debug: Resources: {resources}")
    print(f"Debug: Cooperation rates: {cooperation_rate}")
    print(f"Debug: Betrayal rates: {betrayal_rate}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot resources
    index = np.arange(2)
    bar_width = 0.35
    bars1 = ax1.bar(index, resources, bar_width, color=['green', 'orange'])
    ax1.set_xlabel('Players')
    ax1.set_ylabel('Total Resources')
    ax1.set_title('Best vs Worst Player (Resources)')
    ax1.set_xticks(index)
    ax1.set_xticklabels([f'Best Player {best_player}', f'Worst Player {worst_player}'])

    # Add resource values on top of bars
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{int(yval)}', ha='center', va='bottom')

    # Plot cooperation and betrayal rates
    bar_width = 0.35
    index = np.arange(2)
    bars2_coop = ax2.bar(index, cooperation_rate, bar_width, color='green', label='Cooperation Rate')
    bars2_betrayal = ax2.bar(index + bar_width, betrayal_rate, bar_width, color='red', label='Betrayal Rate')

    ax2.set_xlabel('Players')
    ax2.set_ylabel('Rate (%)')
    ax2.set_title('Best vs Worst Player (Cooperation/Betrayal Rates)')
    ax2.set_xticks(index + bar_width/2)
    ax2.set_xticklabels([f'Best Player {best_player}', f'Worst Player {worst_player}'])
    ax2.legend()

    # Set y-axis limit for rates
    ax2.set_ylim(0, 100)

    # Add cooperation and betrayal values on top of bars
    for bar in bars2_coop:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.1f}%', ha='center', va='bottom')
    
    for bar in bars2_betrayal:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()
    return fig

def plot_trust_decay_rate(trust_decay_rates):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    players = list(trust_decay_rates.keys())
    values = list(trust_decay_rates.values())
    
    ax.bar(players, values, color='blue')
    for i, v in enumerate(values):
        ax.text(i, v + 0.1, f'{v:.2f}', ha='center')
    ax.set_xlabel('Players')
    ax.set_ylabel('Trust Decay Rate')
    ax.set_title('Trust Decay Rate Per Player')
    plt.tight_layout()
    plt.show()
    return fig

def plot_pre_post_collapse_cooperation(pre_collapse_rate, post_collapse_rate):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.bar(['Pre-Collapse', 'Post-Collapse'], [pre_collapse_rate, post_collapse_rate], color=['green', 'orange'])
    for i, v in enumerate([pre_collapse_rate, post_collapse_rate]):
        ax.text(i, v + 0.5, f'{v:.2f}%', ha='center')
    
    ax.set_xlabel('Condition')
    ax.set_ylabel('Cooperation Rate (%)')
    ax.set_title('Pre- and Post-Collapse Cooperation Rate')
    ax.set_ylim(0, 100)
    plt.show()
    plt.tight_layout()
    return fig