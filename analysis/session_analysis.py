import json
import os
import pandas as pd


def save_sessions_to_json(sessions, output_dir):
    print("Starting to save sessions to JSON files...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for session_id, session_data in sessions.items():
        # Remove 'has_click' key from session_data before saving
        if "has_click" in session_data:
            del session_data["has_click"]
        file_path = os.path.join(output_dir, f"{session_id}.json")
        with open(file_path, "w") as json_file:
            json.dump(session_data, json_file, indent=4)
        print(f"Saved session {session_id} to JSON.")
    print("Finished saving all sessions.")


def categorize_session(session):
    actions = session["actions"]
    iterative = False
    opportunistic = False
    unsystematic = False
    multi_tactical = False

    search_terms = []
    for action in actions:
        if action["action_type"] == "extraction" and action["action_label"].startswith(
            "searchterm"
        ):
            search_terms.append(action["params"])
            if len(search_terms) > 1:
                iterative = True

    document_views = set()
    for action in actions:
        if action["action_type"] == "extraction" and action["action_label"] == "docid":
            if action["params"] not in document_views:
                document_views.add(action["params"])
            else:
                opportunistic = True

    action_types = set(a["action_type"] for a in actions)
    if len(action_types) > 1:
        multi_tactical = True

    previous_type = None
    for action in actions:
        if previous_type and action["action_type"] != previous_type:
            unsystematic = True
            break
        previous_type = action["action_type"]

    is_exploratory = iterative and opportunistic and unsystematic and multi_tactical
    return "Exploratory" if is_exploratory else "Lookup"


def compare_sessions(session_df1, session_df2):
    print("Number of sessions in Dataset 1:", len(session_df1))
    print("Number of sessions in Dataset 2:", len(session_df2))


def compare_session_length(session_df1, session_df2, event_df1, event_df2):
    def get_session_lengths(event_df):
        session_lengths = event_df.groupby("session_id")["cts"].agg(["min", "max"])
        session_lengths["length"] = session_lengths["max"] - session_lengths["min"]
        return session_lengths["length"]

    lengths1 = get_session_lengths(event_df1)
    lengths2 = get_session_lengths(event_df2)

    print("Average session length in Dataset 1:", lengths1.mean())
    print("Average session length in Dataset 2:", lengths2.mean())
    print("Max session length in Dataset 1:", lengths1.max())
    print("Max session length in Dataset 2:", lengths2.max())
    print("Min session length in Dataset 1:", lengths1.min())
    print("Min session length in Dataset 2:", lengths2.min())


def compare_actions_per_session(event_df1, event_df2):
    actions_per_session1 = event_df1["session_id"].value_counts()
    actions_per_session2 = event_df2["session_id"].value_counts()

    print("Average actions per session in Dataset 1:", actions_per_session1.mean())
    print("Average actions per session in Dataset 2:", actions_per_session2.mean())
    print("Max actions per session in Dataset 1:", actions_per_session1.max())
    print("Max actions per session in Dataset 2:", actions_per_session2.max())
    print("Min actions per session in Dataset 1:", actions_per_session1.min())
    print("Min actions per session in Dataset 2:", actions_per_session2.min())


def compare_unique_users(table_df1, table_df2):
    unique_users1 = table_df1["user_id"].nunique()
    unique_users2 = table_df2["user_id"].nunique()

    print("Number of unique users in Dataset 1:", unique_users1)
    print("Number of unique users in Dataset 2:", unique_users2)


# Function to calculate the number of tokens in each query
def calculate_query_tokens(actions):
    tokens_per_query = []
    for action in actions:
        if action["action_label"] in [
            "query_form",
            "searchterm_1",
            "searchterm_2",
            "searchterm_3",
            "searchterm_4",
        ]:
            query = action["params"]
            tokens = len(query.split())  # Split the query by spaces to count words
            tokens_per_query.append(tokens)
    return tokens_per_query


# Function to count queries in a session
def count_queries(actions):
    return sum(1 for action in actions if action["action_label"].startswith("search"))


def calculate_bounce_rate(stats):
    for action, data in stats.items():
        # Ensure there's at least one session for this action to avoid division by zero
        if data["Sessions"] > 0:
            data["Bounce Rate"] = (data["Bounces"] / data["Sessions"]) * 100
        else:
            data["Bounce Rate"] = 0  # If there are no sessions, set bounce rate to 0


# Function to calculate query length in characters and terms
def calculate_query_lengths(actions):
    lengths_chars = []
    lengths_terms = []
    for action in actions:
        if action["action_label"] in [
            "query_form",
            "searchterm_1",
            "searchterm_2",
            "searchterm_3",
            "searchterm_4",
        ]:
            params = action["params"]
            lengths_chars.append(len(params))
            lengths_terms.append(len(params.split()))
    return lengths_chars, lengths_terms


# Function to calculate term diversity
def calculate_term_diversity(actions):
    # Collect all terms from actions that are queries
    all_terms = []
    query_actions = [
        "query_form",
        "searchterm_1",
        "searchterm_2",
        "searchterm_3",
        "searchterm_4",
    ]
    for action in actions:
        if action["action_label"] in query_actions:
            all_terms.extend(action["params"].split())

    # Calculate the number of unique terms
    unique_terms = len(set(all_terms))

    # Count the total number of queries in the session
    query_count = sum(
        1 for action in actions if action["action_label"] in query_actions
    )

    # Calculate term diversity
    return unique_terms / query_count if query_count else 0


# Function to calculate the share of queries with advanced search operators
def calculate_search_operators_share(actions):
    advanced_operators = ["AND", "OR", "NOT", '"', "(", ")", "*", "?"]
    queries_with_operators = 0
    for action in actions:
        if action["action_label"].startswith("search"):
            if any(op in action["params"] for op in advanced_operators):
                queries_with_operators += 1
    total_queries = count_queries(actions)
    return (queries_with_operators / total_queries) * 100 if total_queries else 0
