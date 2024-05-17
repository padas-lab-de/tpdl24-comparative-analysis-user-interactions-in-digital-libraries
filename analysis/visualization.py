import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from analysis.utils import remove_extreme_outliers


def generate_boxplots(csv_file_path, output_image_path):
    df = pd.read_csv(csv_file_path)
    max_search_duration = 2000
    df = df[df["search_duration"] <= max_search_duration]
    sns.set(style="ticks", rc={"axes.facecolor": (0, 0, 0, 0)})
    session_colors = {"Exploratory": "#e67e22", "Lookup": "#2980b9"}
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    plot_configs = [
        ("search_depth", "Average search depth (pages)"),
        ("search_duration", "Search duration (seconds)"),
        ("results_pageviews", "Results pageviews per search"),
        ("query_length", "Query length (words)"),
    ]
    for metric, title in plot_configs:
        filtered_df = remove_extreme_outliers(df, metric, "session_type")
        ax = axes[
            plot_configs.index((metric, title)) // 2,
            plot_configs.index((metric, title)) % 2,
        ]
        sns.boxplot(
            ax=ax,
            x=metric,
            y="session_type",
            hue="session_type",
            data=filtered_df,
            palette=session_colors,
            showfliers=False,
            legend=False,
        )
        ax.set_title(title)
        ax.set_ylabel("")
        ax.set_xlabel("")
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()


def compare_action_distribution(event_df1, event_df2):
    action_dist1 = event_df1["action"].value_counts()
    action_dist2 = event_df2["action"].value_counts()

    action_dist = pd.DataFrame(
        {"Dataset 1": action_dist1, "Dataset 2": action_dist2}
    ).fillna(0)

    action_dist.plot(kind="bar", figsize=(15, 7))
    plt.title("Action Distribution Comparison")
    plt.xlabel("Action")
    plt.ylabel("Count")
    plt.show()


def plot_query_distribution(
    all_capped_query_counts, datasets_name, colors, edgecolors, labels
):
    """
    Plots the distribution of queries per user for each dataset.

    Parameters:
    - all_capped_query_counts: List of lists containing the capped query counts for each dataset.
    - datasets_name: List of dataset names.
    - colors: List of colors for each dataset.
    - edgecolors: List of edge colors for each dataset.
    - labels: List of labels for each dataset.
    """
    plt.figure(figsize=(10, 6))
    bins = range(1, 12)  # Adjust as necessary

    for i, dataset in enumerate(datasets_name):
        plt.hist(
            all_capped_query_counts[i],
            bins=bins,
            edgecolor=edgecolors[i],
            color=colors[i],
            label=labels[i],
            density=True,
            alpha=0.5,
            align="left",
        )

    plt.title("Combined Distribution of Queries per User")
    plt.xlabel("Number of Queries (10+ aggregated)")
    plt.ylabel("Proportion of Users")
    plt.xticks(range(1, 12))
    plt.legend()
    plt.tight_layout()
    plt.savefig("metrics/combined_query_distribution.png")
    plt.close()


def plot_tokens_per_query_distribution(
    all_capped_tokens_per_query, datasets_name, colors, edgecolors, labels
):
    """
    Plots the distribution of query lengths by the number of tokens for each dataset.

    Parameters:
    - all_capped_tokens_per_query: List of lists containing the capped tokens per query for each dataset.
    - datasets_name: List of dataset names.
    - colors: List of colors for each dataset.
    - edgecolors: List of edge colors for each dataset.
    - labels: List of labels for each dataset.
    """
    plt.figure(figsize=(10, 6))
    bins = range(1, 23)  # Adjust as necessary

    for i, dataset in enumerate(datasets_name):
        plt.hist(
            all_capped_tokens_per_query[i],
            bins=bins,
            edgecolor=edgecolors[i],
            color=colors[i],
            label=labels[i],
            density=True,
            alpha=0.5,
            align="left",
        )

    plt.title("Combined Distribution of Query Lengths by Number of Tokens")
    plt.xlabel("Number of Tokens in a Query")
    plt.ylabel("Proportion of Queries")
    plt.xticks(ticks=range(1, 22), labels=[str(i) for i in range(1, 21)] + ["20+"])
    plt.legend()
    plt.tight_layout()
    plt.savefig("metrics/combined_tokens_per_query_distribution.png")
    plt.close()
