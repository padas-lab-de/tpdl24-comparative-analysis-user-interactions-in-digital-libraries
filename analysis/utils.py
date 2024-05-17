import json
import pandas as pd
import re
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from nltk.corpus import stopwords
from datetime import datetime


# Utility function to flatten nested dictionaries
def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Utility function to get the number of lines in a file
def get_num_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return sum(1 for line in f)


def remove_extreme_outliers(data, column, category_column):
    Q1 = data.groupby(category_column)[column].quantile(0.25)
    Q3 = data.groupby(category_column)[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_whisker = Q1 - 0.5 * IQR
    upper_whisker = Q3 + 0.5 * IQR
    filtered_data = data[
        (data[column] >= data[category_column].map(lower_whisker))
        & (data[column] <= data[category_column].map(upper_whisker))
    ]
    return filtered_data


def extract_queries(logs):
    queries = []
    search_patterns = ["q", "query", "search"]
    for log in logs:
        if "data" in log:
            data = log["data"]
            urls = []
            if "url" in data:
                urls.append(data["url"])
            if "href" in data:
                urls.append(data["href"])
            for url in urls:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                for param in search_patterns:
                    if param in query_params:
                        queries.extend(query_params[param])
    return queries


def standardize_query(query):
    return re.sub(r"\s+", " ", query).strip()


def rewrite_query(query):
    stop_words = set(stopwords.words("english"))
    words = query.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    rewritten_query = " ".join(filtered_words)
    return rewritten_query


def parse_date(date_str):
    """Parse a date string into a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


# Load environment variables
def load_env_vars():
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")


def load_session(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def get_mapping(action, action_mapping):
    import random

    mappings = action_mapping.get(action, [])
    if mappings:
        return random.choice(mappings)
    else:
        return action


def calculate_session_duration(session):
    start_date = datetime.strptime(session["start_date"], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(session["end_date"], "%Y-%m-%d %H:%M:%S")
    duration = end_date - start_date
    return duration.total_seconds() / 60  # Convert to minutes


def minutes_to_hh_mm(minutes):
    hours = int(minutes // 60)
    minutes = int(minutes % 60)
    return f"{hours:02d}:{minutes:02d}"
