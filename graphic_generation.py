import matplotlib.pyplot as plt
import numpy as np

plt.style.use('classic')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

def generate_plots(metrics, n_rounds):
    plots = {}
    plots['overall_cooperation'] = plot_overall_cooperation(metrics['overall_cooperation_rate'], n_rounds)
    plots['overall_betrayal'] = plot_overall_betrayal(metrics['overall_betrayal_rate'], n_rounds)
    plots['cooperation_per_player'] = plot_cooperation_per_player(metrics['cooperation_per_player'])
    plots['betrayal_per_player'] = plot_betrayal_per_player(metrics['betrayal_per_player'])
    plots['best_worst_cooperation_betrayal'] = plot_best_worst_cooperation_betrayal(metrics)
    
    return plots

def plot_overall_cooperation(cooperation_rates, n_rounds):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(1, n_rounds + 1), cooperation_rates, color='#1f77b4', linewidth=2)
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Cooperation Rate (%)', fontsize=12)
    ax.set_title('Overall Cooperation Rate Over Time', fontsize=14, fontweight='bold')
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)
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
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    return fig

def plot_cooperation_per_player(cooperation_rates):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(cooperation_rates.keys(), cooperation_rates.values(), color='green')
    ax.set_xlabel('Player', fontsize=12)
    ax.set_ylabel('Cooperation Rate (%)', fontsize=12)
    ax.set_title('Cooperation Rate Per Player', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    return fig

def plot_betrayal_per_player(betrayal_rates):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(betrayal_rates.keys(), betrayal_rates.values(), color='orange')
    ax.set_xlabel('Player', fontsize=12)
    ax.set_ylabel('Betrayal Rate (%)', fontsize=12)
    ax.set_title('Betrayal Rate Per Player', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    return fig

def plot_best_worst_cooperation_betrayal(best_worst_data):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    # Cooperation Rate Barplot
    ax[0].bar(
        ['Best Player', 'Worst Player'], 
        [best_worst_data['best_cooperation_rate'], best_worst_data['worst_cooperation_rate']],
        color=['green', 'red']
    )
    ax[0].set_ylim(0, 100)
    ax[0].set_ylabel('Cooperation Rate (%)')
    ax[0].set_title('Cooperation Rate of Best and Worst Players')
    
    # Annotate the resource count on top of bars
    ax[0].text(0, best_worst_data['best_cooperation_rate'] + 2, 
               f'{best_worst_data["best_player_resources"]} resources', ha='center')
    ax[0].text(1, best_worst_data['worst_cooperation_rate'] + 2, 
               f'{best_worst_data["worst_player_resources"]} resources', ha='center')

    # Betrayal Rate Barplot
    ax[1].bar(
        ['Best Player', 'Worst Player'], 
        [best_worst_data['best_betrayal_rate'], best_worst_data['worst_betrayal_rate']],
        color=['blue', 'orange']
    )
    ax[1].set_ylim(0, 100)
    ax[1].set_ylabel('Betrayal Rate (%)')
    ax[1].set_title('Betrayal Rate of Best and Worst Players')
    
    # Annotate the resource count on top of bars
    ax[1].text(0, best_worst_data['best_betrayal_rate'] + 2, 
               f'{best_worst_data["best_player_resources"]} resources', ha='center')
    ax[1].text(1, best_worst_data['worst_betrayal_rate'] + 2, 
               f'{best_worst_data["worst_player_resources"]} resources', ha='center')
    
    plt.tight_layout()
    plt.show()
    return fig
