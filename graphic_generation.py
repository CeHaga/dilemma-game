#gaussian_filter1d: A function for applying a Gaussian filter to 1D data for smoothing.
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.ndimage import gaussian_filter1d

#Set the plotting style to "classic" for a traditional appearance.
#Configure font settings to use "Times New Roman" for the plots.
plt.style.use("classic")
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]

'''
#Function to set a common style for all plots.
    ax: The axis object to apply styles to.
    title: The title of the plot.
    xlabel: The label for the x-axis.
    ylabel: The label for the y-axis.
'''

def set_common_style(ax, title, xlabel, ylabel):
    #Set title and axis labels with custom font size and padding.
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel(xlabel, fontsize=14, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=14, labelpad=10)
    
    #Adjust tick parameters for axis.
    ax.tick_params(axis="both", which="major", labelsize=12)

    #Hide the top and right spines to make the plot cleaner.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

'''
#Function to generate multiple plots based on game metrics.
    metrics: A dictionary of calculated metrics from the game.
    n_rounds: The total number of rounds in the game.
    game_instance: The current game instance.
    game_data: The raw game data used to create plots.
'''
def generate_plots(metrics, n_rounds, game_instance, game_data):
    #Initialize an empty dictionary to hold the generated plots.
    plots = {}

    #Generate the plot for overall cooperation rate.
    plots["overall_cooperation"] = plot_overall_cooperation(
        metrics["overall_cooperation_rate"], n_rounds
    )

    #Generate the plot for overall betrayal rate.
    plots["overall_betrayal"] = plot_overall_betrayal(
        metrics["overall_betrayal_rate"], n_rounds
    )

    #Generate the plot for cooperation and betrayal per player.
    plots["cooperation_betrayal_per_player"] = plot_cooperation_betrayal_per_player(
        metrics["cooperation_per_player"], metrics["betrayal_per_player"]
    )

    #Generate a comparison plot for the best and worst players.
    plots["best_vs_worst"] = plot_best_vs_worst_comparison(
        metrics["best_player"],
        metrics["worst_player"],
        metrics["best_player_data"],
        metrics["worst_player_data"],
    )

    #Generate the plot for trust decay rate.
    plots["trust_decay"] = plot_trust_decay_rate(metrics["trust_decay_rate"])

    #Generate the plot showing the impact of system collapse on cooperation rates.
    plots["collapse_impact"] = plot_pre_post_collapse_cooperation(
        metrics["pre_collapse_cooperation"], metrics["post_collapse_cooperation"]
    )

    #Generate the plot showing how resources evolved over time.
    plots["resources_over_time"] = plot_resources_over_time(
        metrics["resources_over_time"], n_rounds
    )

    #Generate the plot showing the evolution of betrayal probability over time.
    plots['overall_betrayal_probability_evolution'] = plot_overall_betrayal_probability_evolution(game_data)

    #Generate a comparison plot of betrayal probability evolution for the best and worst players.
    plots['best_worst_betrayal_probability_evolution'] = plot_best_worst_betrayal_probability_evolution(
        game_data, metrics['best_player'], metrics['worst_player']
    )

    #Return the dictionary containing all generated plots.
    return plots


'''
#Function to plot the overall cooperation rate over time.
    cooperation_rates: A list of cooperation rates for each round.
    n_rounds: The total number of rounds in the game.
'''
def plot_overall_cooperation(cooperation_rates, n_rounds):
    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Plot the cooperation rates for each round.
    ax.plot(range(1, n_rounds + 1), cooperation_rates, color="#2827d6", linewidth=2.5)

    #Set the title, x-label, and y-label using the common style function.
    set_common_style(
        ax, "Overall Cooperation Rate Over Time", "Round Number", "Cooperation Rate (%)"
    )

    #Set the x and y axis limits.
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)

    #Fill the area under the line to enhance visualization.
    ax.fill_between(range(1, n_rounds + 1), cooperation_rates, alpha=0.3)

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot the overall betrayal rate over time.
    betrayal_rates: A list of betrayal rates for each round.
    n_rounds: The total number of rounds in the game.
'''

def plot_overall_betrayal(betrayal_rates, n_rounds):
    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Plot the betrayal rates for each round.
    ax.plot(range(1, n_rounds + 1), betrayal_rates, color="#d62728", linewidth=2.5)

    #Set the title, x-label, and y-label using the common style function.
    set_common_style(
        ax, "Overall Betrayal Rate Over Time", "Round Number", "Betrayal Rate (%)"
    )

    #Set the x and y axis limits.
    ax.set_xlim(1, n_rounds)
    ax.set_ylim(0, 100)

    #Fill the area under the line to enhance visualization.
    ax.fill_between(range(1, n_rounds + 1), betrayal_rates, alpha=0.3, color="#d62728")

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot cooperation and betrayal counts for each player.
    cooperation_rates: A dictionary containing the cooperation count for each player.
    betrayal_rates: A dictionary containing the betrayal count for each player.
'''

def plot_cooperation_betrayal_per_player(cooperation_rates, betrayal_rates):
    #Create subplots for cooperation and betrayal plots.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    #Sort players based on their player IDs (converted to integers).
    players = sorted(cooperation_rates.keys(), key=lambda x: int(x))

    #Extract cooperation and betrayal values for each player.
    cooperation_values = [cooperation_rates[player] for player in players]
    betrayal_values = [betrayal_rates[player] for player in players]

    #Plot cooperation counts using a bar chart.
    sns.barplot(x=players, y=cooperation_values, ax=ax1, color="#2ca02c", order=players)
    set_common_style(
        ax1, "Cooperation Count Per Player", "Player ID", "Cooperation Count"
    )
    ax1.set_ylim(0, max(cooperation_values) * 1.1)

    #Plot betrayal counts using a bar chart.
    sns.barplot(x=players, y=betrayal_values, ax=ax2, color="#d62728", order=players)
    set_common_style(ax2, "Betrayal Count Per Player", "Player ID", "Betrayal Count")
    ax2.set_ylim(0, max(betrayal_values) * 1.1)

    #Add data labels above each bar.
    for ax in [ax1, ax2]:
        for i, v in enumerate(ax.containers[0]):
            ax.text(
                v.get_x() + v.get_width() / 2,
                v.get_height(),
                f"{v.get_height():.0f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot a comparison between the best and worst players.
    best_player: The ID of the best player.
    worst_player: The ID of the worst player.
    best_player_data: The data for the best player (resources, cooperation, and betrayal rates).
    worst_player_data: The data for the worst player (resources, cooperation, and betrayal rates).
'''
def plot_best_vs_worst_comparison(
    best_player, worst_player, best_player_data, worst_player_data
):
    #Create subplots for resource comparison and cooperation/betrayal rates.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    #Define the player IDs and their respective resource values.
    players = [best_player, worst_player]
    resources = [best_player_data["resources"], worst_player_data["resources"]]

    #Plot resources using a bar chart.
    sns.barplot(x=players, y=resources, ax=ax1, palette=["#2ca02c", "#d62728"])
    set_common_style(
        ax1, "Resources: Best vs Worst Player", "Player", "Total Resources"
    )
    ax1.set_ylim(0, max(resources) * 1.1)

    #Plot cooperation and betrayal rates using a bar chart.
    x = np.arange(2)
    width = 0.35
    ax2.bar(
        x - width / 2,
        [best_player_data["cooperation_rate"], worst_player_data["cooperation_rate"]],
        width,
        label="Cooperation Rate",
        color="#2ca02c",
    )
    ax2.bar(
        x + width / 2,
        [best_player_data["betrayal_rate"], worst_player_data["betrayal_rate"]],
        width,
        label="Betrayal Rate",
        color="#d62728",
    )

    #Set common style and adjust x-tick labels.
    set_common_style(
        ax2,
        "Cooperation and Betrayal Rates: Best vs Worst Player",
        "Player",
        "Rate (%)",
    )
    ax2.set_xticks(x)
    ax2.set_xticklabels(players)
    ax2.legend(loc="upper right", fontsize=12)
    ax2.set_ylim(0, 100)

    #Add data labels inside the bars.
    for ax in [ax1, ax2]:
        for i, v in enumerate(ax.containers):
            ax.bar_label(v, label_type="center", fontsize=10)

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot the trust decay rate for each player.
    trust_decay_rates: A dictionary of trust decay rates for each player.
'''
def plot_trust_decay_rate(trust_decay_rates):
    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Sort players based on their player IDs (converted to integers).
    players = sorted(trust_decay_rates.keys(), key=lambda x: int(x))

    #Extract the trust decay values for each player.
    values = [trust_decay_rates[player] for player in players]

    #Plot trust decay rates using a bar chart.
    sns.barplot(x=players, y=values, ax=ax, color="#1f77b4", order=players)
    set_common_style(ax, "Trust Decay Rate Per Player", "Player ID", "Trust Decay Rate")

    #Add data labels above each bar.
    for i, v in enumerate(ax.containers[0]):
        ax.text(
            v.get_x() + v.get_width() / 2,
            v.get_height(),
            f"{v.get_height():.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot the cooperation rate before and after a system collapse.
    pre_collapse_rate: The cooperation rate before the collapse.
    post_collapse_rate: The cooperation rate after the collapse.
'''
def plot_pre_post_collapse_cooperation(pre_collapse_rate, post_collapse_rate):
    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(10, 8))

    #Define the labels and corresponding values for pre- and post-collapse.
    x = ["Pre-Collapse", "Post-Collapse"]
    y = [pre_collapse_rate, post_collapse_rate]

    #Plot the cooperation rates using a bar chart.
    sns.barplot(x=x, y=y, ax=ax, palette=["#2ca02c", "#d62728"])
    set_common_style(
        ax,
        "Pre- and Post-Collapse Cooperation Rate",
        "Condition",
        "Cooperation Rate (%)",
    )
    ax.set_ylim(0, 100)

    #Add data labels above each bar.
    for i, v in enumerate(y):
        ax.text(i, v + 0.5, f"{v:.2f}%", ha="center", va="bottom", fontsize=12)

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to plot the evolution of player resources over time.
    resources_over_time: A dictionary of resource values for each player across rounds.
    n_rounds: The total number of rounds in the game.
'''
def plot_resources_over_time(resources_over_time, n_rounds):
    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Plot the resource values for each player across rounds.
    for player_id, resources in resources_over_time.items():
        ax.plot(range(1, n_rounds + 1), resources, label=f"Player {player_id}")

    #Set the title, x-label, and y-label using the common style function.
    set_common_style(
        ax, "Resources Over Time for Each Player", "Round Number", "Resources"
    )

    #Set the x-axis limit and add a legend to the plot.
    ax.set_xlim(1, n_rounds)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to calculate the betrayal probability for a player based on their Q-table.
    player: The player object whose betrayal probability is being calculated.
    state: The current game state.
'''
def get_betrayal_probability(player, state):
    #Retrieve the Q-values from the player's Q-table for the given state.
    q_values = player.q_table[state]
    
    #Identify the maximum Q-value for betrayal and cooperation actions.
    betray_q = max(q_values[action] for action in q_values if action is not None)
    cooperate_q = q_values[None]
    
    #Calculate the softmax probability for betrayal.
    temperature = 1.0  #Temperature controls the balance between exploration and exploitation.
    exp_betray = np.exp(betray_q / temperature)
    exp_cooperate = np.exp(cooperate_q / temperature)
    
    #Return the normalized probability of betrayal.
    return exp_betray / (exp_betray + exp_cooperate)

'''
#Function to plot the evolution of betrayal probability over time.
    game_data: The raw game data used to calculate betrayal probabilities.
'''
def plot_overall_betrayal_probability_evolution(game_data):
    #Calculate the total number of rounds.
    rounds = len(game_data)

    #Initialize a list to store average betrayal probabilities.
    avg_betrayal_probabilities = []

    #Loop through each round in the game data to calculate betrayal probabilities.
    for round_data in game_data:
        actions = round_data['actions']

        #Calculate the percentage of betrayal actions for the round.
        betrayal_count = sum(1 for action in actions.values() if action is not None)
        avg_betrayal_probability = (betrayal_count / len(actions)) * 100
        avg_betrayal_probabilities.append(avg_betrayal_probability)

    #Apply Gaussian smoothing to the betrayal probabilities.
    smoothed_probabilities = gaussian_filter1d(avg_betrayal_probabilities, sigma=3)

    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Plot the smoothed betrayal probabilities over time.
    ax.plot(range(1, rounds + 1), smoothed_probabilities, color='#d62728', linewidth=2.5)
    ax.set_xlabel('Round Number', fontsize=14)
    ax.set_ylabel('Average Probability of Betrayal (%)', fontsize=14)
    ax.set_title('Evolution of the Average Probability of Betrayal', fontsize=16, fontweight='bold')
    ax.set_xlim(1, rounds)
    ax.set_ylim(0, 100)

    #Add a grid for better readability.
    ax.grid(True, linestyle='--', alpha=0.7)

    #Add a trendline to visualize the overall trend of betrayal probability.
    z = np.polyfit(range(1, rounds + 1), smoothed_probabilities, 1)
    p = np.poly1d(z)
    ax.plot(range(1, rounds + 1), p(range(1, rounds + 1)), "--", color='#1f77b4', linewidth=2, 
            label='Trend')

    #Add a legend to the plot.
    ax.legend(fontsize=12)

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig

'''
#Function to compare the evolution of betrayal probability between the best and worst players.
    game_data: The raw game data used to calculate betrayal probabilities.
    best_player: The ID of the best player.
    worst_player: The ID of the worst player.
'''
def plot_best_worst_betrayal_probability_evolution(game_data, best_player, worst_player):
    #Calculate the total number of rounds.
    rounds = len(game_data)

    #Initialize lists to store betrayal probabilities for the best and worst players.
    best_betrayal_probs = []
    worst_betrayal_probs = []

    #Define the size of the sliding window for probability calculation.
    window_size = min(20, rounds // 5)

    #Loop through each round to calculate betrayal probabilities for the best and worst players.
    for i in range(rounds):
        start = max(0, i - window_size + 1)

        #Calculate the betrayal probability for the best player in the sliding window.
        best_window = [1 if game_data[j]['actions'][str(best_player)] is not None else 0 for j in range(start, i + 1)]
        worst_window = [1 if game_data[j]['actions'][str(worst_player)] is not None else 0 for j in range(start, i + 1)]

        #Append the calculated probabilities to the respective lists.
        best_betrayal_probs.append(sum(best_window) / len(best_window) * 100)
        worst_betrayal_probs.append(sum(worst_window) / len(worst_window) * 100)

    #Apply Gaussian smoothing to the betrayal probabilities.
    best_smoothed = gaussian_filter1d(best_betrayal_probs, sigma=3)
    worst_smoothed = gaussian_filter1d(worst_betrayal_probs, sigma=3)

    #Create a figure and axis for the plot.
    fig, ax = plt.subplots(figsize=(12, 8))

    #Plot the smoothed betrayal probabilities for both players over time.
    ax.plot(range(1, rounds + 1), best_smoothed, color='#2ca02c', linewidth=2.5, 
            label=f'Best Player (ID: {best_player})')
    ax.plot(range(1, rounds + 1), worst_smoothed, color='#d62728', linewidth=2.5, 
            label=f'Worst Player (ID: {worst_player})')

    #Set axis labels and title using the common style.
    ax.set_xlabel('Round Number', fontsize=14)
    ax.set_ylabel('Betrayal Probability (%)', fontsize=14)
    ax.set_title('Evolution of the Probability of Betrayal: Best vs Worst Player', fontsize=16, fontweight='bold')
    ax.set_xlim(1, rounds)
    ax.set_ylim(0, 100)

    #Add a grid for better readability.
    ax.grid(True, linestyle='--', alpha=0.7)

    #Add trendlines for both players to visualize the overall trends.
    for data, color in zip([best_smoothed, worst_smoothed], ['#2ca02c', '#d62728']):
        z = np.polyfit(range(1, rounds + 1), data, 1)
        p = np.poly1d(z)
        ax.plot(range(1, rounds + 1), p(range(1, rounds + 1)), "--", color=color, linewidth=2, alpha=0.7)

    #Add a legend to the plot.
    ax.legend(fontsize=12, loc='upper left')

    #Adjust the layout to fit everything properly.
    plt.tight_layout()

    #Return the figure object.
    return fig
