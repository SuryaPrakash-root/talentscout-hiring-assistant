import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/candidates.json')

def load_candidates():
    """Load candidates from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_candidates(candidates):
    """Save candidates to the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(candidates, f, indent=4)
