import os
import json
import logging

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from config import Config

class MissionStrategyService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"))
                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    print("[Gemini] API Key Loaded", flush=True)
                    print("[Gemini] Model Initialized", flush=True)
                    print("✓ Gemini successfully initialized", flush=True)
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"
            except Exception as e:
                self.model = None
                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    print(f"[Gemini] Error: {e}", flush=True)
                    print("⚠ Running in fallback mode", flush=True)
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"
                logger.error(f"Error configuring Gemini: {e}")
        else:
            self.model = None
            if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                if not self.api_key:
                    print("[Gemini] Error: Gemini_api_key or GEMINI_API_KEY environment variable is missing", flush=True)
                elif not HAS_GENAI:
                    print("[Gemini] Error: google-generativeai package is not installed", flush=True)
                print("⚠ Running in fallback mode", flush=True)
                os.environ["GEMINI_STARTUP_LOGGED"] = "1"

    def recommend_reveal_count(self, task_details, risk_score, completion_rate, days_remaining, mission_count):
        """
        Determines recommended visible locked milestones count (1 to 5) based on timeline risk.
        Input task_details: { 'title': str, 'description': str }
        """
        remaining_missions = mission_count - int(completion_rate * mission_count / 100)
        prompt = f"""
Act as an elite productivity coach. Recommend how many upcoming milestones (1 to 5) the user should see to optimize focus.
Quest Title: {task_details.get('title', 'Goal')}
Description: {task_details.get('description', '')}
Metrics:
- Risk Score: {risk_score}/100
- Completion Rate: {completion_rate}%
- Days Remaining (Urgency): {days_remaining} days
- Total Milestones (Workload): {mission_count}
- Remaining Milestones: {remaining_missions}

Coaching Logic (Consider carefully):
1. **Urgency**: Evaluate days remaining. Less time remaining increases urgency.
2. **Workload**: Look at total and remaining milestones. High total count requires more focus.
3. **Remaining Missions**: If remaining missions count is high relative to remaining days, narrow focus.
4. **Completion Rate**: Low completion rate means user might be stuck; narrow down focus.

Guidelines:
- High risk, low completion rate, high workload (many remaining missions), or high urgency (days remaining <= 2): Recommend a narrow focus (1-2 visible) to reduce cognitive overload and help them execute.
- Low risk, high progress (high completion rate), low workload, or ample time: Recommend a broader preview (3-5 visible) to aid future sprint planning.

Return ONLY a valid JSON object matching this schema:
{{
  "recommended_reveal_count": int,
  "reason": "string (concise coaching advice detailing why this count was recommended based on urgency, workload, remaining missions, and completion rate)"
}}
Do not wrap in markdown tags like ```json ... ```. Just return raw JSON.
"""
        try:
            if not self.model:
                raise ValueError("Gemini model is not initialized. Please verify your GEMINI_API_KEY environment variable.")
            print("[Gemini] Sending Request", flush=True)
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            text = response.text.strip()
            print("[Gemini] Response Received", flush=True)
            data = json.loads(text)
            # Enforce limits 1 to 5
            count = int(data.get('recommended_reveal_count', 2))
            data['recommended_reveal_count'] = max(1, min(5, count))
            return data
        except Exception as e:
            print(f"[Gemini] Error: {e}", flush=True)
            print("[Gemini] Using Fallback", flush=True)
            return self._recommend_fallback(risk_score, completion_rate, days_remaining)

    def _recommend_fallback(self, risk_score, completion_rate, days_remaining):
        if risk_score >= 70 or completion_rate < 40 or days_remaining <= 2:
            return {
                "recommended_reveal_count": 1,
                "reason": "High execution risk detected. Focus exclusively on the next milestone to prevent cognitive overload."
            }
        elif risk_score >= 40:
            return {
                "recommended_reveal_count": 2,
                "reason": "Moderate risk. Keep focus tight on the next two milestones to make steady progress."
            }
        else:
            return {
                "recommended_reveal_count": 3,
                "reason": "Excellent trajectory. Revealing three milestones to help you coordinate future sprints."
            }

