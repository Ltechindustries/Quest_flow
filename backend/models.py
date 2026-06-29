from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    priority_score = db.Column(db.Integer, default=50)  # 1-100
    risk_score = db.Column(db.Integer, default=0)        # 0-100
    completion_probability = db.Column(db.Float, default=1.0)  # 0.0-1.0
    risk_level = db.Column(db.String(20), default='Low')  # 'Low', 'Medium', 'High'
    risk_explanation = db.Column(db.Text, nullable=True)
    rescue_plan = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Mission
    missions = db.relationship('Mission', backref='task', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        from services.adaptive_reveal_service import determine_reveal_state, get_visible_missions
        from services.cache_service import get_cached_ai_data
        
        # Calculate stats for adaptive reveal
        total = len(self.missions)
        completed = sum(1 for m in self.missions if m.is_completed)
        completion_rate = int((completed / total) * 100) if total > 0 else 100
        
        # Days remaining
        days_remaining = 0
        if self.deadline:
            days_remaining = (self.deadline - datetime.utcnow()).days
            
        stats = {
            "risk_score": self.risk_score,
            "completion_rate": completion_rate,
            "days_remaining": days_remaining
        }
        
        reveal_state = determine_reveal_state(stats)
        
        # Log Adaptive Reveal Updated event (deduplicated internally)
        from services.decision_timeline_service import add_event
        add_event(
            self.id,
            "adaptive_reveal_updated",
            "Atlas Guidance Updated",
            f"Revealed count set to {reveal_state['reveal_count']} based on Atlas Assessment score {stats['risk_score']} and progress completion rate {stats['completion_rate']}%."
        )

        visible_missions = get_visible_missions(self.missions, reveal_state['reveal_count'])

        # Retrieve cached or newly generated AI insights (Reasoning Engine, Daily Brief, Today's Mission)
        ai_data = get_cached_ai_data(self)

        from services.atlas_memory_service import get_memory_summary
        memory_summary = get_memory_summary()

        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() + 'Z' if self.deadline else None,
            'priority_score': self.priority_score,
            'risk_score': self.risk_score,
            'completion_probability': self.completion_probability,
            'risk_level': self.risk_level,
            'risk_explanation': self.risk_explanation,
            'rescue_plan': self.rescue_plan,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'missions': [m.to_dict() for m in sorted(visible_missions, key=lambda x: x.order_index)],
            'explanation': ai_data.get('explanation'),
            'daily_brief': ai_data.get('daily_brief'),
            'todays_mission': ai_data.get('todays_mission'),
            'atlas_profile': memory_summary.get('profile')
        }

        if reveal_state.get('rescue_required'):
            data['rescue_required'] = True

        return data

class Mission(db.Model):
    __tablename__ = 'missions'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    is_unlocked = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'order_index': self.order_index,
            'is_unlocked': self.is_unlocked,
            'is_completed': self.is_completed
        }
