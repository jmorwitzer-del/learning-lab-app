import pandas as pd
from datetime import datetime
import os

JOURNAL_FILE = "journal.csv"

def load_journal():
    if not os.path.exists(JOURNAL_FILE):
        return pd.DataFrame(columns=["timestamp", "entry"])
    return pd.read_csv(JOURNAL_FILE)

def save_entry(text):
    df = load_journal()
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry": text
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(JOURNAL_FILE, index=False)
    return df
