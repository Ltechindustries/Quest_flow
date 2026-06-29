from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Task, Mission
from services.gemini_service import GeminiService
from services.decision_timeline_service import add_event

tasks_bp = Blueprint('tasks', __name__)
gemini_service = GeminiService()

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """
    Creates a new goal/task, runs Gemini decomposition, and saves tasks & missions.
    """
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description', '')
    deadline_str = data.get('deadline')

    if not title or not deadline_str:
        return jsonify({"error": "Title and deadline are required fields."}), 400

    try:
        # Parse deadline
        clean_deadline_str = deadline_str.replace('Z', '').split('.')[0]
        deadline_dt = datetime.fromisoformat(clean_deadline_str)

        # 1. Ask Gemini to decompose goal into missions
        missions_data = gemini_service.generate_missions(title, description)
        if not missions_data:
            missions_data = [
                {"title": "Initial setup and project kick-off", "order": 1},
                {"title": "Execute core task implementation steps", "order": 2},
                {"title": "Review final outputs and complete work", "order": 3}
            ]

        # 2. Build temporary task context for risk calculation
        temp_task = {
            "title": title,
            "description": description,
            "deadline": deadline_dt,
            "missions": [{"title": m.get("title"), "is_completed": False} for m in missions_data]
        }

        # 3. Analyze timeline risk parameters
        risk_score = 50
        completion_prob = 0.50
        risk_explanation = "Assessment score is based on timeline limits."
        try:
            risk_analysis = gemini_service.analyze_risk(temp_task)
            risk_score = risk_analysis.get('risk_score', 50)
            completion_prob_pct = risk_analysis.get('completion_probability', 50)
            completion_prob = completion_prob_pct / 100.0  # Convert 0-100 to float 0.0 - 1.0
            risk_explanation = risk_analysis.get('reason', '')
        except Exception as e:
            # We already log inside gemini_service. This is an extra safety layer.
            pass

        # Determine risk level based on specifications: Low (>0.75), Medium (0.40 - 0.75), High (<0.40)
        if completion_prob > 0.75:
            risk_level = 'Low'
        elif completion_prob >= 0.40:
            risk_level = 'Medium'
        else:
            risk_level = 'High'

        # Generate rescue plan only if risk is High
        rescue_plan = None
        if risk_level == 'High':
            try:
                rescue_data = gemini_service.generate_rescue_plan(temp_task)
                rescue_plan = rescue_data.get('plan')
            except Exception as e:
                pass

        # Calculate Priority Score based on urgency, effort, and proximity
        priority_score = min(100, max(1, int(risk_score * 0.8 + 20)))

        # Create Task
        new_task = Task(
            title=title,
            description=description,
            deadline=deadline_dt,
            priority_score=priority_score,
            risk_score=risk_score,
            completion_probability=completion_prob,
            risk_level=risk_level,
            risk_explanation=risk_explanation,
            rescue_plan=rescue_plan,
            status='pending'
        )

        db.session.add(new_task)
        db.session.flush()

        # Log AI Decision events for Task creation
        add_event(new_task.id, "goal_created", "Goal Created", f"Quest '{new_task.title}' was successfully forged.")
        add_event(new_task.id, "mission_chain_generated", "Atlas Strategy Generated", f"Decomposed quest into a chain of {len(missions_data)} chronological milestones.")
        add_event(new_task.id, "priority_calculated", "Priority Calculated", f"Assigned priority score of {new_task.priority_score}/100 based on urgency and risk.")
        add_event(new_task.id, "risk_evaluated", "Atlas Assessment Completed", f"Analyzed execution risk score: {new_task.risk_score}/100. Reasoning: {new_task.risk_explanation}")
        add_event(new_task.id, "completion_probability_updated", "Completion Probability Updated", f"Calculated objective completion probability at {int(new_task.completion_probability * 100)}%.")
        if new_task.rescue_plan:
            add_event(new_task.id, "recovery_plan_generated", "Atlas Recovery Strategy Generated", "Constructed Atlas Recovery Strategy due to High timeline risk.")

        # Save missions with order indices
        for m_data in missions_data:
            order = m_data.get('order', 1)
            is_unlocked = (order == 1)
            new_mission = Mission(
                task_id=new_task.id,
                title=m_data.get('title', 'Mission'),
                order_index=order,
                is_unlocked=is_unlocked,
                is_completed=False
            )
            db.session.add(new_mission)

        db.session.commit()
        
        # Record first mission unlock and update memory for this new task
        try:
            from services.atlas_memory_service import record_mission_unlock, update_memory
            unlocked_m = next((m for m in new_task.missions if m.order_index == 1), None)
            if unlocked_m:
                record_mission_unlock(unlocked_m.id)
            update_memory(new_task)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to initialize memory trackers: {ex}")

        return jsonify(new_task.to_dict()), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Failed to create task and generate missions: {str(e)}"}), 500

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retrieves all tasks along with their missions.
    """
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve tasks: {str(e)}"}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Retrieves a single task detail.
    """
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Deletes a task and its missions.
    """
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task successfully deleted."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete task: {str(e)}"}), 500

@tasks_bp.route('/tasks/<int:task_id>/reanalyze', methods=['POST'])
def force_reanalyze(task_id):
    """
    Manually triggers AI reanalysis for a specific task.
    """
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404

    try:
        risk_score = 50
        completion_prob = 0.50
        risk_explanation = "Assessment score is based on timeline limits."
        try:
            risk_analysis = gemini_service.analyze_risk(task)
            risk_score = risk_analysis.get('risk_score', 50)
            completion_prob_pct = risk_analysis.get('completion_probability', 50)
            completion_prob = completion_prob_pct / 100.0
            risk_explanation = risk_analysis.get('reason', '')
        except Exception as e:
            pass

        if completion_prob > 0.75:
            risk_level = 'Low'
        elif completion_prob >= 0.40:
            risk_level = 'Medium'
        else:
            risk_level = 'High'

        rescue_plan = None
        if risk_level == 'High':
            try:
                rescue_data = gemini_service.generate_rescue_plan(task)
                rescue_plan = rescue_data.get('plan')
            except Exception as e:
                pass

        task.priority_score = min(100, max(1, int(risk_score * 0.8 + 20)))
        task.risk_score = risk_score
        task.completion_probability = completion_prob
        task.risk_level = risk_level
        task.risk_explanation = risk_explanation
        task.rescue_plan = rescue_plan

        # Log AI Decision events for reanalysis
        add_event(task.id, "priority_calculated", "Priority Calculated", f"Recalculated priority score to {task.priority_score}/100.")
        add_event(task.id, "risk_evaluated", "Atlas Assessment Completed", f"Re-evaluated risk score to {task.risk_score}/100. Reasoning: {task.risk_explanation}")
        add_event(task.id, "completion_probability_updated", "Completion Probability Updated", f"Recalculated completion probability to {int(task.completion_probability * 100)}%.")
        if task.rescue_plan:
            add_event(task.id, "recovery_plan_generated", "Atlas Recovery Strategy Generated", "Constructed updated Atlas Recovery Strategy due to High timeline risk.")

        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to reanalyze task: {str(e)}"}), 500


@tasks_bp.route('/tasks/<int:task_id>/timeline', methods=['GET'])
def get_task_timeline(task_id):
    """
    Retrieves the decision timeline events for a task.
    """
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
    
    from services.decision_timeline_service import get_timeline
    events = get_timeline(task_id)
    return jsonify(events), 200


@tasks_bp.route('/tasks/<int:task_id>/simulate', methods=['POST'])
def simulate_task(task_id):
    """
    Simulates changes to task parameters without modifying the database.
    """
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404

    data = request.get_json() or {}
    simulated_deadline = data.get('simulated_deadline')
    completed_mission_ids = data.get('completed_mission_ids', [])
    available_hours_per_day = data.get('available_hours_per_day', 8)

    if not simulated_deadline:
        return jsonify({"error": "simulated_deadline is required."}), 400

    try:
        from services.simulation_service import run_simulation
        completed_mission_ids = [int(mid) for mid in completed_mission_ids]
        available_hours_per_day = float(available_hours_per_day)

        simulation_result = run_simulation(
            task,
            simulated_deadline,
            completed_mission_ids,
            available_hours_per_day
        )
        return jsonify(simulation_result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to run simulation: {str(e)}"}), 500


