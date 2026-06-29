import os
import json
import logging
import threading
from datetime import datetime, date
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'atlas_memory.json')
_lock = threading.Lock()

def _load_memory():
    """Loads memory file with locking."""
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        return {
            "unlocked_missions": {},
            "completed_missions": [],
            "tasks": {},
            "profile": None
        }
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure basic structure exists
            for key in ["unlocked_missions", "completed_missions", "tasks", "profile"]:
                if key not in data:
                    data[key] = {} if key != "completed_missions" and key != "profile" else ([] if key == "completed_missions" else None)
            return data
    except Exception as e:
        logger.error(f"Error loading Atlas Memory file: {e}")
        return {
            "unlocked_missions": {},
            "completed_missions": [],
            "tasks": {},
            "profile": None
        }

def _save_memory(data):
    """Saves memory file with locking."""
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving Atlas Memory file: {e}")

def record_mission_unlock(mission_id, timestamp=None):
    """Records the unlock timestamp of a mission."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    m_id_str = str(mission_id)
    with _lock:
        data = _load_memory()
        data["unlocked_missions"][m_id_str] = timestamp.isoformat() + "Z"
        _save_memory(data)

def record_mission_completion(task_id, mission_id, timestamp=None):
    """Records completion of a mission and calculates duration."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    m_id_str = str(mission_id)
    t_id_str = str(task_id)
    
    with _lock:
        data = _load_memory()
        unlock_time_str = data["unlocked_missions"].get(m_id_str)
        duration_seconds = 0
        if unlock_time_str:
            try:
                # Remove Z for parsing
                clean_unlock = unlock_time_str.replace('Z', '').split('.')[0]
                unlock_dt = datetime.fromisoformat(clean_unlock)
                duration_seconds = int((timestamp - unlock_dt).total_seconds())
            except Exception as ex:
                logger.warning(f"Error parsing unlock timestamp {unlock_time_str}: {ex}")
        
        # Add to completed missions
        data["completed_missions"].append({
            "mission_id": int(mission_id),
            "task_id": int(task_id),
            "unlocked_at": unlock_time_str,
            "completed_at": timestamp.isoformat() + "Z",
            "duration_seconds": duration_seconds
        })
        
        # Clean up unlock entry
        if m_id_str in data["unlocked_missions"]:
            del data["unlocked_missions"][m_id_str]
            
        _save_memory(data)

def _classify_category(title, description=""):
    """Heuristic classifier to determine category from task content."""
    text = (title + " " + (description or "")).lower()
    if any(k in text for k in ["code", "build", "programming", "dev", "app", "backend", "frontend", "bug", "deploy"]):
        return "Development"
    if any(k in text for k in ["write", "paper", "thesis", "essay", "draft", "blog", "report"]):
        return "Writing"
    if any(k in text for k in ["research", "study", "learn", "read", "search"]):
        return "Research"
    if any(k in text for k in ["design", "ui", "ux", "figma", "mockup", "logo"]):
        return "Design"
    return "General"

def update_memory(task):
    """
    Called when a task completes or updates.
    Records task details and refreshes the personalization profile.
    """
    t_id_str = str(task.id)
    
    # Calculate completions
    total_missions = len(task.missions)
    completed_missions = sum(1 for m in task.missions if m.is_completed)
    
    with _lock:
        data = _load_memory()
        
        data["tasks"][t_id_str] = {
            "title": task.title,
            "description": task.description or "",
            "category": _classify_category(task.title, task.description),
            "status": task.status,
            "created_at": task.created_at.isoformat() + "Z" if task.created_at else None,
            "completed_at": datetime.utcnow().isoformat() + "Z" if task.status == 'completed' else None,
            "total_missions": total_missions,
            "completed_missions": completed_missions,
            "deadline": task.deadline.isoformat() + "Z" if task.deadline else None,
            "risk_score": task.risk_score
        }
        _save_memory(data)
        
    # Generate profile personalization when a quest is completed
    if task.status == 'completed':
        generate_personalization()

def get_memory_summary():
    """
    Returns aggregated productivity statistics.
    """
    with _lock:
        data = _load_memory()
        
    completed_missions = data.get("completed_missions", [])
    tasks = data.get("tasks", {})
    
    # 1. Average mission completion time
    durations = [m["duration_seconds"] for m in completed_missions if m.get("duration_seconds", 0) > 0]
    avg_mission_time = (sum(durations) / len(durations)) / 60.0 if durations else 0.0 # in minutes
    
    # 2. Average quest completion rate
    rates = []
    for t_id, t in tasks.items():
        total = t.get("total_missions", 0)
        completed = t.get("completed_missions", 0)
        rates.append(completed / total if total > 0 else 1.0)
    avg_quest_completion_rate = sum(rates) / len(rates) if rates else 1.0
    
    # 3. Preferred working hours
    hour_slots = {"Late Night (12 AM - 6 AM)": 0, "Morning (6 AM - 12 PM)": 0, "Afternoon (12 PM - 6 PM)": 0, "Evening (6 PM - 12 AM)": 0}
    for m in completed_missions:
        try:
            clean_time = m["completed_at"].replace('Z', '').split('.')[0]
            dt = datetime.fromisoformat(clean_time)
            h = dt.hour
            if 0 <= h < 6:
                hour_slots["Late Night (12 AM - 6 AM)"] += 1
            elif 6 <= h < 12:
                hour_slots["Morning (6 AM - 12 PM)"] += 1
            elif 12 <= h < 18:
                hour_slots["Afternoon (12 PM - 6 PM)"] += 1
            else:
                hour_slots["Evening (6 PM - 12 AM)"] += 1
        except Exception:
            continue
    
    preferred_hours = "Not available"
    if completed_missions:
        max_slot = max(hour_slots, key=hour_slots.get)
        if hour_slots[max_slot] > 0:
            preferred_hours = max_slot
            
    # 4. Delayed and consistently completed categories
    category_stats = {} # category -> {completed_quests, total_quests, delayed_quests}
    for t_id, t in tasks.items():
        cat = t.get("category", "General")
        if cat not in category_stats:
            category_stats[cat] = {"completed": 0, "total": 0, "delayed": 0}
        
        category_stats[cat]["total"] += 1
        if t.get("status") == "completed":
            category_stats[cat]["completed"] += 1
            
        # Check if delayed (past deadline or completed late)
        is_delayed = False
        deadline_str = t.get("deadline")
        completed_str = t.get("completed_at")
        
        if deadline_str:
            try:
                clean_dl = deadline_str.replace('Z', '').split('.')[0]
                dl_dt = datetime.fromisoformat(clean_dl)
                if completed_str:
                    clean_comp = completed_str.replace('Z', '').split('.')[0]
                    comp_dt = datetime.fromisoformat(clean_comp)
                    if comp_dt > dl_dt:
                        is_delayed = True
                else:
                    if datetime.utcnow() > dl_dt:
                        is_delayed = True
            except Exception:
                pass
                
        if is_delayed or t.get("risk_score", 0) >= 70:
            category_stats[cat]["delayed"] += 1

    consistently_completed = []
    frequently_delayed = []
    for cat, stats in category_stats.items():
        comp_rate = stats["completed"] / stats["total"] if stats["total"] > 0 else 0
        delay_rate = stats["delayed"] / stats["total"] if stats["total"] > 0 else 0
        if comp_rate >= 0.8:
            consistently_completed.append(cat)
        if delay_rate >= 0.4:
            frequently_delayed.append(cat)
            
    # 5. Average daily completion count
    dates_completed = {}
    for m in completed_missions:
        try:
            clean_time = m["completed_at"].replace('Z', '').split('.')[0]
            dt = datetime.fromisoformat(clean_time)
            d_str = dt.date().isoformat()
            dates_completed[d_str] = dates_completed.get(d_str, 0) + 1
        except Exception:
            continue
    avg_daily_count = sum(dates_completed.values()) / len(dates_completed) if dates_completed else 0.0
    
    return {
        "completed_quests_count": sum(1 for t in tasks.values() if t.get("status") == "completed"),
        "completed_milestones_count": len(completed_missions),
        "avg_mission_time": avg_mission_time,
        "avg_quest_completion_rate": avg_quest_completion_rate,
        "preferred_hours": preferred_hours,
        "consistently_completed_categories": consistently_completed,
        "frequently_delayed_categories": frequently_delayed,
        "avg_daily_count": avg_daily_count,
        "profile": data.get("profile")
    }

def generate_personalization():
    """
    Feeds aggregated memory statistics to Gemini to generate the productivity profile.
    Saves the profile back to memory file.
    """
    summary = get_memory_summary()
    
    total_completed_quests = summary["completed_quests_count"]
    total_completed_missions = summary["completed_milestones_count"]
    avg_mission_time = summary["avg_mission_time"]
    avg_quest_completion_rate = summary["avg_quest_completion_rate"]
    preferred_hours = summary["preferred_hours"]
    completed_categories = summary["consistently_completed_categories"]
    delayed_categories = summary["frequently_delayed_categories"]
    avg_daily_count = summary["avg_daily_count"]
    
    prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Analyze the following user productivity statistics derived from their completed quests and milestones:

Productivity Stats:
- Completed Quests: {total_completed_quests}
- Completed Milestones: {total_completed_missions}
- Average Milestone Completion Time: {avg_mission_time:.1f} minutes
- Average Quest Completion Rate: {avg_quest_completion_rate * 100:.1f}%
- Preferred Working Hours: {preferred_hours}
- Consistently Completed Categories: {', '.join(completed_categories) if completed_categories else 'None'}
- Frequently Delayed Categories: {', '.join(delayed_categories) if delayed_categories else 'None'}
- Average Daily Completion Count: {avg_daily_count:.2f}

Based on these statistics, generate a concise productivity profile for the user.
Choose a fitting profile name (e.g. "Deadline Sprinter", "Steady Marathoner", "Night Owl Developer", "Early Bird Researcher").
Keep the strengths, weaknesses, and recommendations professional, calm, concise, encouraging, and tailored to the statistics.

Return ONLY a valid JSON object matching this schema:
{{
  "profile": "string (fitting profile name)",
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "weaknesses": [
    "weakness 1",
    "weakness 2"
  ],
  "recommendations": [
    "recommendation 1",
    "recommendation 2"
  ]
}}
Do not wrap in markdown tags like ```json ... ```. Just return raw JSON.
"""
    gemini = GeminiService()
    try:
        if not gemini.model:
            raise ValueError("Gemini model is not initialized. Please verify your GEMINI_API_KEY environment variable.")
        print("[Gemini] Sending Request", flush=True)
        response = gemini.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        text = response.text.strip()
        print("[Gemini] Response Received", flush=True)
        profile = json.loads(text)
    except Exception as e:
        print(f"[Gemini] Error: {e}", flush=True)
        print("[Gemini] Using Fallback", flush=True)
        profile = _fallback_profile(avg_quest_completion_rate, avg_mission_time, preferred_hours)
        
    # Save the profile to memory JSON
    with _lock:
        data = _load_memory()
        data["profile"] = profile
        _save_memory(data)
        
    return profile

def _fallback_profile(completion_rate, avg_mission_time, preferred_hours):
    """Plausible backup productivity profile generator."""
    if completion_rate < 0.6:
        return {
            "profile": "Deadline Sprinter",
            "strengths": [
                "Capable of high velocity during urgent sprints.",
                "Responsive to recovery strategies."
            ],
            "weaknesses": [
                "Prone to initial quest planning stagnation.",
                "Vulnerable to timeline deficits."
            ],
            "recommendations": [
                "Establish milestones with conservative durations.",
                "Initiate active missions early in your cycle."
            ]
        }
    else:
        return {
            "profile": "Steady Marathoner",
            "strengths": [
                "Maintains consistent milestone velocity.",
                "Strong overall quest completion rate."
            ],
            "weaknesses": [
                "May over-allocate time to low-impact tasks.",
                "Reluctant to delay low-priority milestones."
            ],
            "recommendations": [
                "Focus on the single high-impact target daily.",
                "Delegate or delay secondary cosmetic objectives."
            ]
        }
