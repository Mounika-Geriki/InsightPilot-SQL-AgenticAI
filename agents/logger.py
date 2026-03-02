import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("agent_logs.json")

def log_execution(question, intent, confidence):

    record = {
        "timestamp": str(datetime.utcnow()),
        "question": question,
        "intent": intent,
        "confidence": confidence
    }

    if LOG_FILE.exists():
        data = json.loads(LOG_FILE.read_text())
    else:
        data = []

    data.append(record)
    LOG_FILE.write_text(json.dumps(data, indent=2))
