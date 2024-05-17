import csv
import json
from datetime import datetime

def parse_csv(file_path):
    sessions = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            session_id = row['session_id']
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "session_length": int(row['session_length']),
                    "user_id": int(row['user_id']),
                    "start_date": row['date'],
                    "end_date": row['date'],
                    "actions": []
                }
            action = {
                "action_id": int(row['id']),
                "timestamp": row['date'],
                "action_type": row['mapping_type'],
                "action_label": row['mapping_action_label'],
                "action_length": int(row['action_length']),
                "params": row['params'],
                "origin_action": row['origin_action']
            }
            sessions[session_id]['actions'].append(action)
            if datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S") > datetime.strptime(sessions[session_id]['end_date'], "%Y-%m-%d %H:%M:%S"):
                sessions[session_id]['end_date'] = row['date']
    return sessions

def save_sessions_to_json(sessions, output_dir):
    for session_id, session_data in sessions.items():
        file_path = f"{output_dir}/{session_id}.json"
        with open(file_path, 'w') as json_file:
            json.dump(session_data, json_file, indent=4)