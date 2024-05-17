import argparse
import random
import os
import json
from datetime import datetime

from analysis.utils import load_session
from analysis.session_generation import create_synthetic_session
from analysis.suss_processing import parse_csv, save_sessions_to_json
from analysis.visualization import (
    compare_action_distribution,
    generate_boxplots,
    plot_query_distribution,
    plot_tokens_per_query_distribution,
)
from analysis.data_processing import (
    load_dataset,
    extract_events_sessions,
    extract_table_data,
    process_large_json_to_csv_ndjson,
    parse_sessions,
    process_sessions_to_csv,
    load_action_mappings,
    human_readable_to_session,
    process_sessions,
    categorize_and_compute_stats,
)
from analysis.session_analysis import (
    compare_sessions,
    compare_session_length,
    compare_actions_per_session,
    compare_unique_users,
    save_sessions_to_json,
)


def generate_synthetic_sessions():
    session_start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Starting session generation at:", session_start_date)

    # Read topics from file and select one randomly
    with open("data/synthetic_queries.txt", "r", encoding="utf-8") as file:
        topics = file.readlines()
    print(f"Loaded {len(topics)} topics.")

    action_mappings = load_action_mappings("data/suss/action_mapping.csv")
    print(f"Loaded {len(action_mappings)} action mappings.")

    original_sessions_dir = "data/econbiz/original_sessions/"
    synthetic_sessions_dir = "data/econbiz/synthetic_sessions/"

    original_files = os.listdir(original_sessions_dir)
    print(f"Found {len(original_files)} original session files to process.")

    for filename in original_files:
        print(f"Processing file: {filename}")
        original_session = load_session(os.path.join(original_sessions_dir, filename))

        synthetic_topic = random.choice(topics).strip()
        print(
            f"Selected synthetic topic: {synthetic_topic[:50]}..."
        )  # Print a portion of the topic to keep the log concise

        synthetic_session = create_synthetic_session(
            original_session, synthetic_topic, action_mappings
        )

        synthetic_file_path_txt = os.path.join(
            synthetic_sessions_dir, f"synthetic_{filename}.txt"
        )
        with open(synthetic_file_path_txt, "w") as file:
            file.write(synthetic_session)
        print(f"Synthetic session written to TXT: {synthetic_file_path_txt}")

        session_json = human_readable_to_session(synthetic_session, session_start_date)
        json_subfolder_path = os.path.join(synthetic_sessions_dir, "json")
        os.makedirs(json_subfolder_path, exist_ok=True)

        synthetic_file_path_json = os.path.join(
            json_subfolder_path, f"synthetic_{filename}.json"
        )
        with open(synthetic_file_path_json, "w") as file:
            json.dump(session_json, file, indent=4)
        print(f"Synthetic session JSON stored: {synthetic_file_path_json}\n")

    print("All sessions processed successfully.")


def process_suss(csv_file_path, output_dir):
    sessions = parse_csv(csv_file_path)
    save_sessions_to_json(sessions, output_dir)
    print("SUSS sessions processed and saved to JSON.")


def load_datasets():
    dataset1 = load_dataset("data/suss/sessions/")
    dataset2 = load_dataset("data/econbiz/sessions/")

    # Extract sessions and events
    sessions1, events1 = extract_events_sessions(dataset1)
    sessions2, events2 = extract_events_sessions(dataset2)

    # Load table data
    table1 = extract_table_data(dataset1)
    table2 = extract_table_data(dataset2)

    return sessions1, sessions2, events1, events2, table1, table2


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser = argparse.ArgumentParser(description="Data Analysis Tools")
    parser = argparse.ArgumentParser(description="Session Data Analysis")
    parser = argparse.ArgumentParser(description="Topology Interaction Analysis")
    parser = argparse.ArgumentParser(
        description="Session Data Analysis and Synthetic Session Generation"
    )
    parser = argparse.ArgumentParser(
        description="Run comparative analysis on session data."
    )
    parser = argparse.ArgumentParser(
        description="Data processing for SUSS and other datasets."
    )

    # Add arguments
    parser.add_argument(
        "--generate-synthetic",
        action="store_true",
        help="Generate synthetic session data",
    )
    parser.add_argument(
        "--json-to-csv",
        action="store_true",
        help="Process JSON file and convert it to CSV",
    )
    parser.add_argument(
        "--generate-boxplots",
        action="store_true",
        help="Generate boxplots for session analysis",
    )
    parser.add_argument(
        "--process-sessions",
        action="store_true",
        help="Parse session data and save to JSON",
    )
    parser.add_argument(
        "--process-classification",
        action="store_true",
        help="Process session data and output to CSV",
    )
    parser.add_argument(
        "--compare-sessions",
        action="store_true",
        help="Compare basic session info between two datasets",
    )
    parser.add_argument(
        "--compare-length",
        action="store_true",
        help="Compare session lengths between two datasets",
    )
    parser.add_argument(
        "--compare-actions",
        action="store_true",
        help="Compare actions per session between two datasets",
    )
    parser.add_argument(
        "--compare-users",
        action="store_true",
        help="Compare unique users between two datasets",
    )
    parser.add_argument(
        "--compare-distribution",
        action="store_true",
        help="Compare action distribution between two datasets",
    )
    parser.add_argument(
        "--process-suss",
        action="store_true",
        help="Process SUSS dataset CSV and save sessions to JSON",
    )
    parser.add_argument("--csv-file-path", type=str, help="Path to the SUSS CSV file")
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save the processed SUSS sessions JSON files",
    )
    parser.add_argument("--process", action="store_true", help="Process session data")
    parser.add_argument("--visualize", action="store_true", help="Visualize data")

    # Parse arguments
    args = parser.parse_args()

    # '--json-to-csv' (for EconBiz data)
    if args.process_json_to_csv:
        file_path = "data/econbiz/sessions.json"
        output_csv_path = "data/econbiz/sessions.csv"
        process_large_json_to_csv_ndjson(file_path, output_csv_path)
        print("JSON to CSV processing completed.")

    # '--generate-boxplots'
    if args.generate_boxplots:
        csv_file_path = "logs/suss/sessions_analysis.csv"
        output_image_path = "metrics/sessions_analysis_suss.png"
        generate_boxplots(csv_file_path, output_image_path)
        print("Boxplots generated.")

    # '--process-sessions'
    if args.process_sessions:
        if not args.json_file_path or not args.output_dir:
            print(
                "Both --json-file-path and --output-dir are required for session processing."
            )
            return
        parse_sessions(args.json_file_path)
        save_sessions_to_json(args.json_file_path, args.output_dir)
        print("Session processing completed.")

    # '--process-classification'
    if args.process_sessions:
        directory = "data/suss/sessions/"
        csv_file_path = "logs/suss/sessions_analysis.csv"
        process_sessions_to_csv(directory, csv_file_path)

    # '--generate'
    if args.generate:
        generate_synthetic_sessions()

    if args.process_suss and args.csv_file_path and args.output_dir:
        process_suss(args.csv_file_path, args.output_dir)

    # '--compare-XXXX'
    if args.compare_sessions:
        sessions1, sessions2, events1, events2, table1, table2 = load_datasets()
        compare_sessions(sessions1, sessions2)

    if args.compare_length:
        sessions1, sessions2, events1, events2, table1, table2 = load_datasets()
        compare_session_length(sessions1, sessions2, events1, events2)

    if args.compare_actions:
        sessions1, sessions2, events1, events2, table1, table2 = load_datasets()
        compare_actions_per_session(events1, events2)

    if args.compare_users:
        sessions1, sessions2, events1, events2, table1, table2 = load_datasets()
        compare_unique_users(table1, table2)

    if args.compare_distribution:
        sessions1, sessions2, events1, events2, table1, table2 = load_datasets()
        compare_action_distribution(events1, events2)

    if args.process:
        data_directory = "data/suss/sessions/"
        dataset_name = "suss"
        process_sessions(data_directory, dataset_name)
        categorize_and_compute_stats(data_directory, dataset_name)

    if args.visualize:
        datasets = {"suss": "data/suss/sessions/", "econbiz": "data/econbiz/sessions/"}
        # Initialize as lists of lists for each dataset
        all_capped_query_counts = [[] for _ in datasets]
        all_capped_tokens_per_query = [[] for _ in datasets]

        i = 0
        for dataset_name, data_directory in datasets.items():
            print(f"Processing dataset: {dataset_name}")
            stats_df = categorize_and_compute_stats(data_directory, dataset_name)
            output_directory = f"metrics/{dataset_name}/"
            os.makedirs(output_directory, exist_ok=True)
            stats_df.to_csv(
                f"{output_directory}topology_interaction_{dataset_name}.csv",
                index=False,
            )
            print(
                f"Data saved to {output_directory}topology_interaction_{dataset_name}.csv"
            )

            # Collect data for plotting
            capped_query_counts, capped_tokens_per_query = process_sessions(
                data_directory, dataset_name
            )
            all_capped_query_counts[i] = capped_query_counts
            all_capped_tokens_per_query[i] = capped_tokens_per_query
            i += 1

        datasets_name = ["suss", "econbiz"]
        colors = ["#1abc9c", "#e74c3c"]
        edgecolors = ["#16a085", "#c0392b"]
        labels = ["SUSS", "EconBiz"]

        plot_query_distribution(
            all_capped_query_counts, datasets_name, colors, edgecolors, labels
        )
        plot_tokens_per_query_distribution(
            all_capped_tokens_per_query, datasets_name, colors, edgecolors, labels
        )
        print("Visualization completed.")


if __name__ == "__main__":
    main()
