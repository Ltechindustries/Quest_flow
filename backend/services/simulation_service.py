import os
import json
import logging
from datetime import datetime
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

def run_simulation(task, simulated_deadline_str, completed_mission_ids, available_hours_per_day):
    """
    Simulates a task's trajectory based on a simulated deadline, simulated completed mission IDs,
    and available hours per day. Returns a simulated outcome without updating the database.
    """
    title = getattr(task, 'title', task.get('title') if isinstance(task, dict) else '')
    description = getattr(task, 'description', task.get('description') if isinstance(task, dict) else '')
    
    # Parse simulated deadline
    now = datetime.utcnow()
    try:
        clean_dl = simulated_deadline_str.replace('Z', '').split('.')[0]
        simulated_deadline = datetime.fromisoformat(clean_dl)
    except Exception as ex:
        logger.error(f"Failed to parse simulated deadline {simulated_deadline_str}: {ex}")
        simulated_deadline = now

    # Extract missions and mark their simulated completion state
    missions = getattr(task, 'missions', task.get('missions') if isinstance(task, dict) else [])
    
    simulated_missions = []
    for m in missions:
        m_id = getattr(m, 'id', m.get('id') if isinstance(m, dict) else None)
        m_title = getattr(m, 'title', m.get('title') if isinstance(m, dict) else '')
        
        # Simulated as completed if it was already completed or is in the simulated completed list
        is_completed_already = getattr(m, 'is_completed', m.get('is_completed') if isinstance(m, dict) else False)
        is_sim_completed = is_completed_already or (m_id in completed_mission_ids)
        
        simulated_missions.append({
            "id": m_id,
            "title": m_title,
            "is_completed": is_sim_completed
        })

    # Prepare stats for prompt
    total_missions = len(simulated_missions)
    sim_completed_count = sum(1 for m in simulated_missions if m["is_completed"])
    sim_remaining_count = total_missions - sim_completed_count
    
    time_left_seconds = (simulated_deadline - now).total_seconds()
    time_left_days = max(0.0, time_left_seconds / 86400.0)
    time_left_hours_total = time_left_days * available_hours_per_day
    
    # Format missions state for the prompt
    missions_summary = []
    for idx, m in enumerate(simulated_missions):
        state = "Completed" if m["is_completed"] else "Incomplete"
        missions_summary.append(f"{idx+1}. {m['title']} ({state})")
    missions_str = "\n".join(missions_summary)

    prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Simulate changes to this quest and evaluate the execution timeline under these simulated parameters:

Quest: {title}
Description: {description}
Simulated Deadline: {simulated_deadline.isoformat()}
Days Remaining: {time_left_days:.2f} days
Estimated Available Hours Per Day: {available_hours_per_day} hours/day
Total Simulated Available Time: {time_left_hours_total:.1f} hours

Milestones (with simulated completion states):
{missions_str}

Evaluate the simulation and calculate:
1. "new_completion_probability": integer (0 to 100) representing completion chance under these parameters.
2. "new_risk_score": integer (0 to 100) representing the risk score.
3. "risk_level": "Low" (if probability > 75%), "Medium" (if probability between 40% and 75%), or "High" (if probability < 40%).
4. "recommended_schedule": A list of short strings outlining a logical day-by-day or step-by-step recovery plan / milestones timeline to complete the {sim_remaining_count} remaining incomplete milestones given the {time_left_hours_total:.1f} total hours available.
5. "summary": A concise, encouraging, and coaching-focused summary of the simulation results. Focus on the impact of changing the deadline or completing milestones.
6. "recommendations": A list of 2-3 specific recommendations for execution (e.g. daily focus, hour allocations, scope-cuts).

Your tone must be calm, concise, and professional. Avoid emojis.

Return ONLY a JSON object matching this schema:
{{
  "new_completion_probability": 85,
  "new_risk_score": 15,
  "risk_level": "Low",
  "recommended_schedule": [
    "Day 1: Focus on milestone X",
    "Day 2: Complete milestone Y"
  ],
  "summary": "Coaching overview...",
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
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
        # Secondary check to unwrap markdown block if the model ignores the instruction
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except Exception as e:
        print(f"[Gemini] Error: {e}", flush=True)
        print("[Gemini] Using Fallback", flush=True)
        return _run_fallback_simulation(
            title, simulated_missions, time_left_days, available_hours_per_day
        )

def _run_fallback_simulation(title, simulated_missions, time_left_days, available_hours_per_day):
    total = len(simulated_missions)
    completed = sum(1 for m in simulated_missions if m["is_completed"])
    remaining = total - completed
    
    # 1.5 hours estimated per remaining mission
    hours_needed = remaining * 1.5
    hours_available = time_left_days * available_hours_per_day
    
    if time_left_days <= 0:
        completion_prob = 0
        risk_score = 100
        risk_level = "High"
    elif remaining == 0:
        completion_prob = 100
        risk_score = 0
        risk_level = "Low"
    else:
        ratio = hours_available / hours_needed if hours_needed > 0 else 1.0
        if ratio >= 1.5:
            completion_prob = 95
            risk_score = 10
            risk_level = "Low"
        elif ratio >= 1.0:
            completion_prob = 80
            risk_score = 25
            risk_level = "Low"
        elif ratio >= 0.6:
            completion_prob = 55
            risk_score = 55
            risk_level = "Medium"
        else:
            completion_prob = 25
            risk_score = 85
            risk_level = "High"
            
    # Generate schedule
    schedule = []
    remaining_missions = [m for m in simulated_missions if not m["is_completed"]]
    if remaining_missions:
        if time_left_days <= 0:
            schedule.append("Critical: Deadline has passed. Immediate intervention required.")
        else:
            # Spread remaining missions over the days
            days_step = max(1.0, time_left_days / len(remaining_missions))
            for idx, m in enumerate(remaining_missions):
                day_num = int((idx + 1) * days_step)
                schedule.append(f"Day {day_num}: Focus on '{m['title']}'")
    else:
        schedule.append("All milestones simulated as completed. Timeline is secure.")
        
    # Generate summary
    if time_left_days <= 0:
        summary = f"Timeline parameters indicate high deficit. The simulated deadline has already elapsed."
    else:
        summary = f"Simulating quest execution over {time_left_days:.1f} remaining days with {available_hours_per_day} hours/day. The target trajectory reports {risk_level.lower()} risk."
        
    # Generate recommendations
    recommendations = []
    if risk_level == "High":
        recommendations.append("Apply timeline expansion immediately or scope-cut secondary tasks.")
        recommendations.append("Dedicate high-priority deep focus blocks to the next milestone.")
    elif risk_level == "Medium":
        recommendations.append("Track daily completion rate carefully to avoid late-stage bottlenecks.")
        recommendations.append("Ensure at least one milestone is cleared every day.")
    else:
        recommendations.append("Current parameters are optimal. Maintain steady execution pace.")
        recommendations.append("Consider accelerating early milestones to secure buffer time.")
        
    return {
        "new_completion_probability": completion_prob,
        "new_risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_schedule": schedule,
        "summary": summary,
        "recommendations": recommendations
    }
