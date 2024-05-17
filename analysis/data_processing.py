import csv
from tqdm import tqdm
import json
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from analysis.utils import (
    extract_queries,
    standardize_query,
    rewrite_query,
    flatten_dict,
    parse_date,
    calculate_session_duration,
    get_num_lines,
    minutes_to_hh_mm,
)
import os
import pandas as pd
from analysis.session_analysis import (
    categorize_session,
    calculate_query_tokens,
    count_queries,
    calculate_query_lengths,
    calculate_term_diversity,
    calculate_search_operators_share,
    calculate_bounce_rate,
)


action_mappings = {
    "CTS_search": "Access Point",
    "CTS_select": "Access Point",
    "delete_comment": "Drop-off",
    "export_bib": "Object",
    "export_cite": "Object",
    "export_mail": "Object",
    "export_search_mail": "Object",
    "goto_about": "Lookup",
    "goto_advanced_search": "Access Point",
    "goto_advanced_search_reconf": "Access Point",
    "goto_contribute": "Access Point",
    "goto_create_account": "Transactional",
    "goto_delete_account": "Transactional",
    "goto_edit_password": "Transactional",
    "goto_favorites": "Access Point",
    "goto_fulltext": "Object",
    "goto_google_books": "Object",
    "goto_google_scholar": "Object",
    "goto_history": "Access Point",
    "goto_home": "Access Point",
    "goto_impressum": "Lookup",
    "goto_last_search": "Access Point",
    "goto_local_availability": "Object",
    "goto_login": "Transactional",
    "goto_partner": "Lookup",
    "goto_sofis": "Lookup",
    "goto_team": "Lookup",
    "goto_thesaurus": "Access Point",
    "goto_topic-feeds": "Access Point",
    "goto_topic-research": "Access Point",
    "goto_topic-research-unique": "Access Point",
    "purge_history": "Drop-off",
    "save_search": "Transactional",
    "save_search_history": "Transactional",
    "save_to_multiple_favorites": "Transactional",
    "search": "Access Point",
    "search_advanced": "Access Point",
    "search_as_rss": "Access Point",
    "search_change_facets": "Access Point",
    "search_change_nohts": "Access Point",
    "search_change_nohts_2": "Access Point",
    "search_change_only_fulltext": "Access Point",
    "search_change_only_fulltext_2": "Access Point",
    "search_change_paging": "Access Point",
    "search_change_sorting": "Access Point",
    "search_from_history": "Access Point",
    "search_institution": "Access Point",
    "search_keyword": "Access Point",
    "search_person": "Access Point",
    "search_thesaurus": "Access Point",
    "to_favorites": "Transactional",
    "view_citation": "Lookup",
    "view_comment": "Lookup",
    "view_description": "Lookup",
    "view_record": "Object",
    "view_references": "Lookup",
    "view_doc_rec": "Object",
    "query_form": "Access Point",
}


# Function to discover fields for NDJSON
def discover_fields_ndjson(file_path):
    fields = set()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in tqdm(
            file, total=get_num_lines(file_path), desc="Discovering Fields"
        ):
            obj = json.loads(line)
            flat_entry = flatten_dict(obj)
            fields.update(flat_entry.keys())
    return list(fields)


# Function to process NDJSON file and write to CSV
def process_large_json_to_csv_ndjson(file_path, output_csv_path):
    fields = discover_fields_ndjson(file_path)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

        with open(file_path, "r", encoding="utf-8") as file:
            for line in tqdm(file, total=get_num_lines(file_path), desc="Writing CSV"):
                obj = json.loads(line)
                flat_entry = flatten_dict(obj)
                writer.writerow(flat_entry)


def parse_sessions(file_path):
    import ijson  # Import here to limit its scope to this function

    sessions = {}
    last_click_action_type = None
    last_action_timestamp = {}
    print("Starting to parse sessions...")

    with open(file_path, "rb") as file:
        for line in file:

            session = next(ijson.items(line, ""))
            session_id = session["session_id"]

            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "session_length": 0,
                    "user_id": -1,
                    "start_date": None,
                    "end_date": None,
                    "actions": [],
                    "has_click": False,
                }
                last_action_timestamp[session_id] = None
                last_click_action_type = None

            for event in session.get("events", []):
                action_timestamp = datetime.utcfromtimestamp(event["cts"] / 1000)
                action_formatted_timestamp = action_timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                if last_action_timestamp[session_id] is not None:
                    action_length = int(
                        (
                            action_timestamp - last_action_timestamp[session_id]
                        ).total_seconds()
                    )
                else:
                    action_length = 0

                action = {
                    "action_id": event.get("cts", None),
                    "timestamp": action_formatted_timestamp,
                    "action_type": event["category"],
                    "action_label": event["action"],
                    "action_length": action_length,
                    "params": event.get("params", ""),
                    "origin_action": event.get("origin_action", ""),
                }

                # Handling params for RecordMLT and PageView
                if action["action_type"] == "RecordMLT":
                    action["params"] = ",".join(
                        map(str, event.get("data", {}).get("record_ids", []))
                    )
                elif action["action_type"] == "PageView":
                    action["params"] = event.get("page_view_id", "")

                # Handling params for AvailabilityButton with click action_label
                if (
                    action["action_type"] == "AvailabilityButton"
                    and action["action_label"] == "click"
                ):
                    queries = extract_queries([event])
                    standardized_queries = [
                        standardize_query(query) for query in queries
                    ]
                    rewritten_queries = [
                        rewrite_query(query) for query in standardized_queries
                    ]
                    action["params"] = ",".join(rewritten_queries)

                if action["action_label"] == "click":
                    sessions[session_id]["has_click"] = True
                    if last_click_action_type is not None:
                        action["origin_action"] = last_click_action_type
                    last_click_action_type = action["action_type"]

                sessions[session_id]["actions"].append(action)

                if (
                    not sessions[session_id]["start_date"]
                    or action["timestamp"] < sessions[session_id]["start_date"]
                ):
                    sessions[session_id]["start_date"] = action["timestamp"]

                if (
                    not sessions[session_id]["end_date"]
                    or action["timestamp"] > sessions[session_id]["end_date"]
                ):
                    sessions[session_id]["end_date"] = action["timestamp"]

                last_action_timestamp[session_id] = action_timestamp

            if sessions[session_id]["start_date"] and sessions[session_id]["end_date"]:
                session_start = datetime.strptime(
                    sessions[session_id]["start_date"], "%Y-%m-%d %H:%M:%S"
                )
                session_end = datetime.strptime(
                    sessions[session_id]["end_date"], "%Y-%m-%d %H:%M:%S"
                )
                sessions[session_id]["session_length"] = int(
                    (session_end - session_start).total_seconds()
                )

    print("Finished parsing sessions.")
    return {sid: sess for sid, sess in sessions.items() if sess["has_click"]}


def process_sessions_to_csv(directory, csv_file_path):
    session_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
            session_id = data["session_id"]
            start_date = parse_date(data["start_date"])
            end_date = parse_date(data["end_date"])
            search_duration = (end_date - start_date).total_seconds()
            session_type = categorize_session(data)

            search_depth = 0
            results_pageviews = 0
            total_query_length = 0
            search_actions = 0
            search_refinements = 0
            first_action = True

            # Analyze actions to derive additional metrics
            viewed_docs = set()
            search_terms = []

            for action in data["actions"]:
                if action["action_label"] == "view_record":
                    search_depth += 1
                    viewed_docs.add(action["params"])
                if action["action_type"] == "extraction" and action[
                    "action_label"
                ].startswith("searchterm_"):
                    search_terms.append(action["params"])
                    total_query_length += len(action["params"].split())
                    search_actions += 1
                if (
                    (
                        action["action_type"] == "action"
                        and action["action_label"].startswith("search")
                    )
                    or (
                        action["action_type"] == "action"
                        and action["action_label"].startswith("query")
                    )
                ) and not first_action:
                    search_refinements += 1
                if action["action_label"] == "resultlistids":
                    results_pageviews += len(action["params"].split(","))
                first_action = False

            # Calculate metrics
            percent_search_refinements = (
                search_refinements / search_depth if search_depth else 0
            )

            session_data.append(
                {
                    "session_id": session_id,
                    "session_type": session_type,
                    "search_depth": search_depth,
                    "results_pageviews": results_pageviews,
                    "search_duration": search_duration,
                    "percent_search_refinements": percent_search_refinements,
                    "query_length": total_query_length,
                }
            )

    df = pd.DataFrame(session_data)
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    df.to_csv(csv_file_path, index=False)
    print(f"CSV file has been created at {csv_file_path}")


def load_action_mappings(csv_file_path):
    action_mappings = []
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            action_mappings.append(row)
    return action_mappings


def session_to_human_readable(session):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    previous_timestamp = datetime.strptime(session["start_date"], datetime_format)
    human_readable_description = []
    for action in session["actions"]:
        current_timestamp = datetime.strptime(action["timestamp"], datetime_format)
        time_spent = (current_timestamp - previous_timestamp).total_seconds()
        action_description = f"Time spent: {time_spent} seconds; Action Type: {action['action_type']}; Action Label: {action['action_label']}"
        if action["params"]:
            action_description += f"; Params: {action['params']}"
        human_readable_description.append(action_description)
        previous_timestamp = current_timestamp
    return "\n".join(human_readable_description)


def human_readable_to_session(
    human_readable_str, session_start_date, user_id=-1, end_date=None
):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    start_datetime = datetime.strptime(session_start_date, datetime_format)
    lines = human_readable_str.strip().split("\n")
    actions = []
    current_datetime = start_datetime
    for line in lines:
        match = re.match(
            r"Time spent: (\d+\.\d+|\d+) seconds; Action Type: (.*?); Action Label: (.*?)(; Params: (.*))?$",
            line,
        )
        if not match:
            continue
        time_spent, action_type, action_label, _, params_str = match.groups()
        current_datetime += timedelta(seconds=float(time_spent))
        timestamp = current_datetime.strftime(datetime_format)
        params = {}
        if params_str:
            params_parts = params_str.split("; ")
            for part in params_parts:
                if ": " in part:
                    key, value = part.split(": ", 1)
                    params[key] = value.strip('"')
        action_dict = {
            "timestamp": timestamp,
            "action_type": action_type,
            "action_label": action_label,
            "params": params,
        }
        actions.append(action_dict)
    session_length = (current_datetime - start_datetime).total_seconds()
    if not end_date:
        end_date = current_datetime.strftime(datetime_format)
    session_dict = {
        "session_length": session_length,
        "user_id": user_id,
        "start_date": session_start_date,
        "end_date": end_date,
        "actions": actions,
    }
    return session_dict


def load_dataset(directory_path):
    sessions = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read().strip()
                if not file_content:
                    continue
                try:
                    session_data = json.loads(file_content)
                except json.JSONDecodeError:
                    continue
            sessions.extend(session_data)
    return sessions


def extract_events_sessions(data):
    sessions = []
    events = []
    for session in data:
        session_id = session["session_id"]
        sessions.append(
            {
                "session_id": session_id,
                "has_duplicate_pids": session["has_duplicate_pids"],
                "supports_beacon": session["supports_beacon"],
                "n_errors": session["n_errors"],
            }
        )
        for event in session["events"]:
            events.append(
                {
                    "session_id": session_id,
                    "action": event["action"],
                    "category": event["category"],
                    "cts": event["cts"],
                    "data": event.get("data", {}),
                }
            )
    return pd.DataFrame(sessions), pd.DataFrame(events)


def extract_table_data(data):
    return pd.DataFrame(data)


# Function to process all sessions and compute statistics
def process_sessions(data_directory, dataset_name):
    output_file = f"metrics/{dataset_name}/session_metrics_{dataset_name}.txt"

    session_durations = []
    query_counts = []
    query_lengths_chars = []
    query_lengths_terms = []
    term_diversities = []
    search_operators_shares = []
    queries_to_tokens_ratios = []
    all_query_tokens = []
    query_counts_per_session = []

    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            with open(os.path.join(data_directory, filename), "r") as file:
                session = json.load(file)
                session_durations.append(calculate_session_duration(session))
                query_counts.append(count_queries(session["actions"]))
                lengths_chars, lengths_terms = calculate_query_lengths(
                    session["actions"]
                )
                query_lengths_chars.extend(lengths_chars)
                query_lengths_terms.extend(lengths_terms)
                term_diversities.append(calculate_term_diversity(session["actions"]))
                search_operators_shares.append(
                    calculate_search_operators_share(session["actions"])
                )
                query_tokens = calculate_query_tokens(session["actions"])
                all_query_tokens.extend(query_tokens)
                query_count = count_queries(session["actions"])
                query_counts_per_session.append(query_count)

                # Calculate the total number of tokens (terms)
                total_tokens = sum(
                    len(action["params"].split())
                    for action in session["actions"]
                    if action["action_label"]
                    in [
                        "query_form",
                        "searchterm_1",
                        "searchterm_2",
                        "searchterm_3",
                        "searchterm_4",
                    ]
                )
                # Calculate the ratio of queries to tokens if total_tokens is not zero
                if total_tokens > 0:
                    ratio = query_count / total_tokens
                    queries_to_tokens_ratios.append(ratio)

    capped_query_counts = [min(count, 10) for count in query_counts_per_session]
    capped_tokens_per_query = [min(tokens, 20) for tokens in all_query_tokens]

    # Calculate mean, median, and standard deviation for each metric
    metrics = {
        "Session Duration (hh:mm)": {
            "Mean": mean(session_durations) if session_durations else 0,
            "Median": median(session_durations) if session_durations else 0,
            "SD": stdev(session_durations) if len(session_durations) > 1 else 0,
        },
        "Query Count": {
            "Mean": mean(query_counts) if query_counts else 0,
            "Median": median(query_counts) if query_counts else 0,
            "SD": stdev(query_counts) if len(query_counts) > 1 else 0,
        },
        "Query Length (#chars)": {
            "Mean": mean(query_lengths_chars) if query_lengths_chars else 0,
            "Median": median(query_lengths_chars) if query_lengths_chars else 0,
            "SD": stdev(query_lengths_chars) if len(query_lengths_chars) > 1 else 0,
        },
        "Query Length (#terms)": {
            "Mean": mean(query_lengths_terms) if query_lengths_terms else 0,
            "Median": median(query_lengths_terms) if query_lengths_terms else 0,
            "SD": stdev(query_lengths_terms) if len(query_lengths_terms) > 1 else 0,
        },
        "Term Diversity": {
            "Mean": mean(term_diversities) if term_diversities else 0,
            "Median": median(term_diversities) if term_diversities else 0,
            "SD": stdev(term_diversities) if len(term_diversities) > 1 else 0,
        },
        "Search Operators Share": {
            "Mean": mean(search_operators_shares) if search_operators_shares else 0,
            "Median": median(search_operators_shares) if search_operators_shares else 0,
            "SD": (
                stdev(search_operators_shares)
                if len(search_operators_shares) > 1
                else 0
            ),
        },
    }

    # Calculate the average session duration in minutes
    average_duration_minutes = mean(session_durations)

    # Convert the average duration to "hh:mm" format
    average_duration_hh_mm = minutes_to_hh_mm(average_duration_minutes)

    # Check if the output file already exists before writing
    if not os.path.exists(output_file):
        with open(output_file, "w") as f:
            f.write("Session Metrics Summary:\n")
            f.write("========================\n")
            f.write(f"Average Session Duration (hh:mm): {average_duration_hh_mm}\n\n")

            for metric, values in metrics.items():
                f.write(f"{metric}:\n")
                if isinstance(values, dict):  # For metrics stored as dictionaries
                    f.write(f"  Mean    = {values.get('Mean', 0):.2f}\n")
                    f.write(f"  Median  = {values.get('Median', 0):.2f}\n")
                    f.write(f"  SD      = {values.get('SD', 0):.2f}\n\n")
                else:
                    f.write(
                        f"  Value   = {values}\n\n"
                    )  # For metrics stored as single values
    else:
        print(f"Skipping writing as {output_file} already exists.")

    return capped_query_counts, capped_tokens_per_query


def categorize_and_compute_stats(data_directory, dataset_name):
    stats = {
        action: {
            "Page Views": 0,
            "Total Time": timedelta(),
            "Entrances": 0,
            "Bounces": 0,
            "Exits": 0,
            "Sessions": 0,
        }
        for action in action_mappings.keys()
    }

    for filename in sorted(os.listdir(data_directory)):

        if filename.endswith(".json"):
            with open(os.path.join(data_directory, filename), "r") as file:
                session_data = json.load(file)
                actions_in_session = set()

                # Track if the session is a bounce (only one action in the session)
                is_bounce = len(session_data["actions"]) == 1

                for action in session_data["actions"]:
                    action_label = action["action_label"]
                    if action_label in action_mappings:
                        actions_in_session.add(action_label)
                        action_length = timedelta(seconds=action["action_length"])
                        stats[action_label]["Total Time"] += action_length
                        if action["origin_action"] == "":
                            stats[action_label]["Entrances"] += 1
                            stats[action_label][
                                "Sessions"
                            ] += 1  # Increment session count for this action
                        if is_bounce:
                            stats[action_label]["Bounces"] += 1
                        # Check if the action is the last in the session for % Exit calculation
                        if action == session_data["actions"][-1]:
                            stats[action_label]["Exits"] += 1

                for action_label in actions_in_session:
                    stats[action_label]["Page Views"] += 1

    calculate_bounce_rate(stats)
    # Convert the stats dictionary to a list of dictionaries for DataFrame creation
    stats_list = []
    for action, data in stats.items():
        stats_list.append(
            {
                "Action": action,
                "Page Views": data["Page Views"],
                "Avg. Time": (
                    str(data["Total Time"] / data["Page Views"])
                    if data["Page Views"] > 0
                    else "0:00"
                ),
                "Entrances": data["Entrances"],
                "Bounce Rate": f"{data['Bounce Rate']:.2f}%",
                "% Exit": f"{(data['Exits'] / data['Page Views']) * 100 if data['Page Views'] > 0 else 0:.2f}%",
            }
        )

    return pd.DataFrame(stats_list)
