import uuid
from datetime import datetime
import threading

_timeline = {}
_lock = threading.Lock()

def add_event(task_id, event_type, title, description):
    """
    Adds a decision timeline event for the given task.
    Supports basic deduplication for 'adaptive_reveal_updated' events to prevent spamming.
    """
    task_id_str = str(task_id)
    with _lock:
        if task_id_str not in _timeline:
            _timeline[task_id_str] = []
        
        # Deduplication for adaptive_reveal_updated
        if event_type == "adaptive_reveal_updated":
            last_event = None
            for ev in reversed(_timeline[task_id_str]):
                if ev["type"] == "adaptive_reveal_updated":
                    last_event = ev
                    break
            if last_event and last_event["description"] == description:
                return last_event

        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            "title": title,
            "description": description
        }
        _timeline[task_id_str].append(event)
        return event

def get_timeline(task_id):
    """
    Retrieves the decision timeline for a given task, sorted newest first.
    """
    task_id_str = str(task_id)
    with _lock:
        events = _timeline.get(task_id_str, [])
        # Return a copy sorted newest first
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)
