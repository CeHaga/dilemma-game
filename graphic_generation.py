import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.style.use('classic')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

def set_common_style(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=14, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=14, labelpad=10)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

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
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(range(1, n_rounds + 1), cooperation_rates, color='#1f77b4', linewidth=2.5)
    set_common_style(ax, 'Overall Cooperation Rate Over Time', 'Round Number', 'Cooperation Rate (%)')
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)
    ax.fill_between(range(1, n_rounds + 1), cooperation_rates, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return fig

def plot_overall_betrayal(betrayal_rates, n_rounds):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(range(1, n_rounds + 1), betrayal_rates, color='#d62728', linewidth=2.5)
    set_common_style(ax, 'Overall Betrayal Rate Over Time', 'Round Number', 'Betrayal Rate (%)')
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)
    ax.fill_between(range(1, n_rounds + 1), betrayal_rates, alpha=0.3, color='#d62728')
    plt.tight_layout()
    plt.show()
    return fig

def plot_cooperation_betrayal_per_player(cooperation_rates, betrayal_rates):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    players = sorted(cooperation_rates.keys(), key=lambda x: int(x))
    cooperation_values = [cooperation_rates[player] for player in players]
    betrayal_values = [betrayal_rates[player] for player in players]
    
    # Cooperation plot
    sns.barplot(x=players, y=cooperation_values, ax=ax1, color='#2ca02c', order=players)
    set_common_style(ax1, 'Cooperation Count Per Player', 'Player ID', 'Cooperation Count')
    ax1.set_ylim(0, max(cooperation_values) * 1.1)
    
    # Betrayal plot
    sns.barplot(x=players, y=betrayal_values, ax=ax2, color='#d62728', order=players)
    set_common_style(ax2, 'Betrayal Count Per Player', 'Player ID', 'Betrayal Count')
    ax2.set_ylim(0, max(betrayal_values) * 1.1)
    
    for ax in [ax1, ax2]:
        for i, v in enumerate(ax.containers[0]):
            ax.text(v.get_x() + v.get_width()/2, v.get_height(), f'{v.get_height():.0f}', 
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    return fig

def plot_best_vs_worst_comparison(best_player, worst_player, best_player_data, worst_player_data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Resources plot
    players = [best_player, worst_player]
    resources = [best_player_data['resources'], worst_player_data['resources']]
    sns.barplot(x=players, y=resources, ax=ax1, palette=['#2ca02c', '#d62728'])
    set_common_style(ax1, 'Resources: Best vs Worst Player', 'Player', 'Total Resources')
    ax1.set_ylim(0, max(resources) * 1.1)
    
    # Rates plot
    x = np.arange(2)
    width = 0.35
    ax2.bar(x - width/2, [best_player_data['cooperation_rate'], worst_player_data['cooperation_rate']], 
            width, label='Cooperation Rate', color='#2ca02c')
    ax2.bar(x + width/2, [best_player_data['betrayal_rate'], worst_player_data['betrayal_rate']], 
            width, label='Betrayal Rate', color='#d62728')
    
    set_common_style(ax2, 'Cooperation and Betrayal Rates: Best vs Worst Player', 'Player', 'Rate (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(players)
    ax2.legend(loc='upper right', fontsize=12)
    ax2.set_ylim(0, 100)
    
    for ax in [ax1, ax2]:
        for i, v in enumerate(ax.containers):
            ax.bar_label(v, label_type='center', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    return fig

def plot_trust_decay_rate(trust_decay_rates):
    fig, ax = plt.subplots(figsize=(12, 8))
    players = sorted(trust_decay_rates.keys(), key=lambda x: int(x))
    values = [trust_decay_rates[player] for player in players]
    
    sns.barplot(x=players, y=values, ax=ax, color='#1f77b4', order=players)
    set_common_style(ax, 'Trust Decay Rate Per Player', 'Player ID', 'Trust Decay Rate')
    
    for i, v in enumerate(ax.containers[0]):
        ax.text(v.get_x() + v.get_width()/2, v.get_height(), f'{v.get_height():.2f}', 
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    return fig

def plot_pre_post_collapse_cooperation(pre_collapse_rate, post_collapse_rate):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    x = ['Pre-Collapse', 'Post-Collapse']
    y = [pre_collapse_rate, post_collapse_rate]
    sns.barplot(x=x, y=y, ax=ax, palette=['#2ca02c', '#d62728'])
    set_common_style(ax, 'Pre- and Post-Collapse Cooperation Rate', 'Condition', 'Cooperation Rate (%)')
    ax.set_ylim(0, 100)
    
    for i, v in enumerate(y):
        ax.text(i, v + 0.5, f'{v:.2f}%', ha='center', va='bottom', fontsize=12)
    
    plt.tight_layout()
    plt.show()
    return fig