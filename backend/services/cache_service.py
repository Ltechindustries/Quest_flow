import os
import json
import logging
from datetime import datetime
from services.gemini_service import GeminiService
from services.explanation_service import ExplanationService
from services.decision_timeline_service import add_event

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'ai_cache.json')

def get_task_state_key(task):
    """
    Constructs a unique state hash key for a task.
    If the task description, status, priority, risk metrics, or any mission status/title changes,
    the key changes, prompting a cache invalidation and AI regeneration.
    """
    missions_state = []
    # Fetch all missions associated with the task
    for m in sorted(task.missions, key=lambda x: x.order_index):
        missions_state.append(f"{m.id}:{m.is_completed}:{m.is_unlocked}:{m.title}")
    
    missions_str = "|".join(missions_state)
    
    # Days remaining calculation
    days_remaining = 0
    if task.deadline:
        # Standardize deadline
        dt = task.deadline
        days_remaining = (dt - datetime.utcnow()).days

    return f"{task.id}:{task.title}:{task.description}:{task.priority_score}:{task.risk_score}:{task.completion_probability}:{task.status}:{days_remaining}:{missions_str}"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading AI cache file: {e}")
        return {}

def save_cache(cache_data):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving AI cache file: {e}")

def get_cached_ai_data(task):
    """
    Retrieves or generates AI insights (explanation, daily brief, today's mission) for a task.
    Only runs Gemini when the task state key changes.
    """
    state_key = get_task_state_key(task)
    cache = load_cache()
    
    task_id_str = str(task.id)
    
    if task_id_str in cache:
        cached_entry = cache[task_id_str]
        if cached_entry.get('state_key') == state_key:
            return {
                "explanation": cached_entry.get('explanation'),
                "daily_brief": cached_entry.get('daily_brief'),
                "todays_mission": cached_entry.get('todays_mission')
            }

    # Cache miss or stale state. Regenerate using Gemini.
    logger.info(f"Cache miss for Task {task.id}. Regenerating AI insights...")
    
    gemini_service = GeminiService()
    explanation_service = ExplanationService()
    
    # Calculate stats
    total = len(task.missions)
    completed = sum(1 for m in task.missions if m.is_completed)
    days_remaining = 0
    if task.deadline:
        days_remaining = (task.deadline - datetime.utcnow()).days
    
    # Format missions lists for services
    missions_list = [m.to_dict() for m in task.missions]

    # Generate details
    explanation = explanation_service.explain_decisions(
        task_title=task.title,
        task_desc=task.description or "",
        missions=missions_list,
        priority=task.priority_score,
        risk_score=task.risk_score,
        completion_prob=task.completion_probability,
        days_remaining=days_remaining
    )

    daily_brief = gemini_service.generate_daily_brief(
        task_title=task.title,
        task_desc=task.description or "",
        missions=missions_list,
        priority=task.priority_score,
        risk_score=task.risk_score,
        completion_prob=task.completion_probability,
        days_remaining=days_remaining
    )

    todays_mission = gemini_service.generate_todays_mission(
        task_title=task.title,
        task_desc=task.description or "",
        missions=missions_list
    )

    # Log Today's Mission Selected event
    add_event(
        task.id,
        "todays_mission_selected",
        "Atlas Focus Selected",
        f"Atlas selected '{todays_mission.get('title')}' as today's highest impact mission. Reason: {todays_mission.get('reason')}"
    )

    # Save to cache
    cache[task_id_str] = {
        "state_key": state_key,
        "explanation": explanation,
        "daily_brief": daily_brief,
        "todays_mission": todays_mission
    }
    save_cache(cache)

    return {
        "explanation": explanation,
        "daily_brief": daily_brief,
        "todays_mission": todays_mission
    }
