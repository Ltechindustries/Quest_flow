import os
import json
import logging
import sys

logger = logging.getLogger(__name__)

# Reconfigure stdout to use UTF-8 on Windows terminals to prevent UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def safe_print(msg):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        msg_ascii = msg.replace("✓", "OK").replace("⚠", "Warning")
        try:
            print(msg_ascii, flush=True)
        except Exception:
            pass

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from config import Config

class ExplanationService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"))
                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    safe_print("[Gemini] API Key Loaded")
                    safe_print("[Gemini] Model Initialized")
                    safe_print("✓ Gemini successfully initialized")
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"
                logger.info("Explanation Service initialized with gemini-3.5-flash.")
            except Exception as e:
                self.model = None
                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    safe_print(f"[Gemini] Error: {e}")
                    safe_print("⚠ Running in fallback mode")
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"
                logger.error(f"Error configuring Gemini SDK in ExplanationService: {e}")
        else:
            self.model = None
            if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                if not self.api_key:
                    safe_print("[Gemini] Error: Gemini_api_key or GEMINI_API_KEY environment variable is missing")
                elif not HAS_GENAI:
                    safe_print("[Gemini] Error: google-generativeai package is not installed")
                safe_print("⚠ Running in fallback mode")
                os.environ["GEMINI_STARTUP_LOGGED"] = "1"


    def explain_decisions(self, task_title, task_desc, missions, priority, risk_score, completion_prob, days_remaining):
        """
        Explains important AI decisions using Gemini.
        Returns:
        {
          "why_this_priority": ["...", "...", "..."],
          "current_risks": ["...", "..."],
          "recommended_focus": ["...", "...", "..."],
          "tasks_to_delay": ["...", "..."]
        }
        """
        missions_summary = [{"title": m.get("title"), "is_completed": m.get("is_completed")} for m in missions]

        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Analyze the following quest configuration and state to generate Atlas Insights:
Quest Title: {task_title}
Description: {task_desc}
Missions: {json.dumps(missions_summary)}
Priority Score: {priority}/100
Risk / Assessment Score: {risk_score}/100
Completion Probability: {completion_prob:.2f}
Days Remaining: {days_remaining}

Explain the decisions made:
1. Why this priority score was assigned.
2. What are the current execution/timeline risks.
3. What is the recommended focus.
4. Which tasks or scope elements should be delayed or postponed.

Return ONLY a valid JSON object matching this schema:
{{
  "why_this_priority": [
    "Explanation sentence 1",
    "Explanation sentence 2",
    "Explanation sentence 3"
  ],
  "current_risks": [
    "Risk description 1",
    "Risk description 2"
  ],
  "recommended_focus": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "tasks_to_delay": [
    "Postponed task or secondary item 1",
    "Postponed task or secondary item 2"
  ]
}}

Constraints:
- "why_this_priority" must contain at most 3 items.
- "current_risks" must contain at most 2 items.
- "recommended_focus" must contain at most 3 items.
- "tasks_to_delay" must contain at most 2 items.
- Keep explanations concise, clear, and highly specific to the quest details.
Do not wrap in markdown tags like ```json ... ```. Just return raw JSON.
"""
        try:
            if not self.model:
                raise ValueError("Gemini model is not initialized. Please verify your GEMINI_API_KEY environment variable.")
            safe_print("[Gemini] Sending Request")
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            text = response.text.strip()
            safe_print("[Gemini] Response Received")
            return json.loads(text)
        except Exception as e:
            safe_print(f"[Gemini] Error: {e}")
            try:
                if not self.model:
                    raise e
                safe_print("[Gemini] Sending Request")
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                safe_print("[Gemini] Response Received")
                if text.startswith("```"):
                    lines = text.split("\n")
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines[-1].startswith("```"): lines = lines[:-1]
                    text = "\n".join(lines).strip()
                return json.loads(text)
            except Exception as e2:
                if self.model:
                    safe_print(f"[Gemini] Error: {e2}")
                safe_print("[Gemini] Using Fallback")
                return self._fallback_explanation(priority, risk_score)

    def _fallback_explanation(self, priority, risk_score):
        return {
            "why_this_priority": [
                f"Priority score of {priority} is aligned with your active deadline constraints and remaining milestones.",
                "Steady progress is recommended to maintain execution momentum."
            ],
            "current_risks": [
                f"An assessment score of {risk_score} highlights minor execution risks.",
                "Ensure that critical dependencies are completed first."
            ],
            "recommended_focus": [
                "I recommend focusing on the current active milestone.",
                "Ensure downstream scope items remain locked to prevent multitasking."
            ],
            "tasks_to_delay": [
                "Postpone cosmetic adjustments until core systems are functional.",
                "Delay secondary code updates to optimize velocity."
            ]
        }
