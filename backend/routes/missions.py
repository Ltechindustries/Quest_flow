from flask import Blueprint, request, jsonify
from models import db, Mission, Task
from services.gemini_service import GeminiService
from services.decision_timeline_service import add_event
from services.atlas_memory_service import record_mission_unlock, record_mission_completion, update_memory

missions_bp = Blueprint('missions', __name__)
gemini_service = GeminiService()

@missions_bp.route('/missions/unlock', methods=['POST'])
def unlock_mission():
    """
    Unlocks a specific mission.
    Accepts JSON body: {"mission_id": <id>} or request parameter ?mission_id=<id>
    """
    data = request.get_json() or {}
    mission_id = data.get('mission_id') or request.args.get('mission_id')

    if not mission_id:
        return jsonify({"error": "mission_id is required in JSON body or as query parameter."}), 400

    mission = Mission.query.get(mission_id)
    if not mission:
        return jsonify({"error": "Mission not found."}), 404

    try:
        mission.is_unlocked = True
        db.session.commit()
        record_mission_unlock(mission.id)
        return jsonify(mission.task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to unlock mission: {str(e)}"}), 500

@missions_bp.route('/missions/complete', methods=['POST'])
def complete_mission():
    """
    Completes a specific mission and unlocks the next chronological mission.
    Accepts JSON body: {"mission_id": <id>} or request parameter ?mission_id=<id>
    """
    data = request.get_json() or {}
    mission_id = data.get('mission_id') or request.args.get('mission_id')

    if not mission_id:
        return jsonify({"error": "mission_id is required in JSON body or as query parameter."}), 400

    return _process_mission_completion(mission_id)

@missions_bp.route('/missions/<int:mission_id>/complete', methods=['POST'])
def complete_mission_by_id(mission_id):
    """
    Fallback endpoint to support URL-path based completion calls from frontend.
    """
    return _process_mission_completion(mission_id)


def _process_mission_completion(mission_id):
    mission = Mission.query.get(mission_id)
    if not mission:
        return jsonify({"error": "Mission not found."}), 404

    if mission.is_completed:
        return jsonify(mission.task.to_dict()), 200

    task = mission.task
    try:
        # Mark current mission as completed
        mission.is_completed = True
        record_mission_completion(task.id, mission.id)

        # Find all missions for this task, ordered by order_index
        all_missions = sorted(task.missions, key=lambda x: x.order_index)
        
        # Unlock the next incomplete mission (progressive reveal)
        next_mission = None
        for m in all_missions:
            if not m.is_completed:
                next_mission = m
                break

        if next_mission:
            next_mission.is_unlocked = True
            record_mission_unlock(next_mission.id)
        else:
            # All missions completed
            task.status = 'completed'

        # Recalculate AI metrics with current progress
        completed_count = sum(1 for m in all_missions if m.is_completed)
        total_count = len(all_missions)

        # Recalculate AI metrics with current progress
        risk_analysis = gemini_service.analyze_risk(task)
        risk_score = risk_analysis.get('risk_score', 0)
        completion_prob_pct = risk_analysis.get('completion_probability', 100)
        completion_prob = completion_prob_pct / 100.0

        if completion_prob > 0.75:
            risk_level = 'Low'
        elif completion_prob >= 0.40:
            risk_level = 'Medium'
        else:
            risk_level = 'High'

        rescue_plan = None
        if risk_level == 'High':
            rescue_data = gemini_service.generate_rescue_plan(task)
            rescue_plan = rescue_data.get('plan')

        task.priority_score = min(100, max(1, int(risk_score * 0.8 + 20)))
        task.risk_score = risk_score
        task.completion_probability = completion_prob
        task.risk_level = risk_level
        task.risk_explanation = risk_analysis.get('reason', '')
        task.rescue_plan = rescue_plan

        # Log AI Decision events for mission completion
        add_event(task.id, "priority_calculated", "Priority Calculated", f"Recalculated priority score to {task.priority_score}/100.")
        add_event(task.id, "risk_evaluated", "Atlas Assessment Completed", f"Re-evaluated risk score to {task.risk_score}/100. Reasoning: {task.risk_explanation}")
        add_event(task.id, "completion_probability_updated", "Completion Probability Updated", f"Recalculated completion probability to {int(task.completion_probability * 100)}%.")
        if task.rescue_plan:
            add_event(task.id, "recovery_plan_generated", "Atlas Recovery Strategy Generated", "Constructed updated Atlas Recovery Strategy due to High timeline risk.")

        db.session.commit()
        update_memory(task)
        return jsonify(task.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to complete mission: {str(e)}"}), 500
