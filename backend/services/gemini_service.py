import os
import json
import logging
import sys
from datetime import datetime

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

class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                # Initialize configured Gemini model
                self.model = genai.GenerativeModel(self.model_name)

                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    safe_print("[Gemini] API Key Loaded")
                    safe_print(f"[Gemini] Model Initialized: {self.model_name}")
                    safe_print("✓ Gemini successfully initialized")
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"

                logger.info(f"Gemini Service initialized with {self.model_name}.")

            except Exception as e:
                self.model = None

                if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                    safe_print(f"[Gemini] Error: {e}")
                    safe_print("⚠ Running in fallback mode")
                    os.environ["GEMINI_STARTUP_LOGGED"] = "1"

                logger.error(f"Error configuring Gemini SDK: {e}")

        else:
            self.model = None

            if not os.environ.get("GEMINI_STARTUP_LOGGED"):
                if not self.api_key:
                    safe_print("[Gemini] Error: GEMINI_API_KEY environment variable is missing")
                elif not HAS_GENAI:
                    safe_print("[Gemini] Error: google-generativeai package is not installed")

                safe_print("⚠ Running in fallback mode")
                os.environ["GEMINI_STARTUP_LOGGED"] = "1"



    def generate_missions(self, goal, description):
        """
        Decomposes a goal into a sequential chain of missions.
        Returns:
        [
         {
          "title": "Mission title",
          "order": 1
         }
        ]
        """
        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Decompose this goal into a logically ordered sequential chain of chronological and highly realistic milestones (missions) as part of Atlas Strategy:
Goal: {goal}
Description: {description}

Ensure that:
- The milestones follow a logical ordering and dependencies.
- Milestones are realistic.
- Each milestone is sized to take between 20 to 90 minutes to complete.
- Provide a maximum of 8 milestones.

Return ONLY a JSON array of objects. Each object MUST have:
- "title": active, specific, and clear milestone task description
- "order": sequential integer starting at 1
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
                return self._generate_missions_fallback(goal)


    def analyze_risk(self, task):
        """
        Analyzes task timeline risk and probability.
        Returns:
        {
         "risk_score": 0-100,
         "completion_probability": 0-100,
         "reason": "..."
        }
        """
        title = getattr(task, 'title', task.get('title') if isinstance(task, dict) else '')
        description = getattr(task, 'description', task.get('description') if isinstance(task, dict) else '')
        deadline = getattr(task, 'deadline', task.get('deadline') if isinstance(task, dict) else None)
        
        now = datetime.now()
        time_left_str = "Unknown"
        time_left_hours = 72.0
        if deadline:
            try:
                if isinstance(deadline, str):
                    clean_dt = deadline.replace('Z', '').split('.')[0]
                    dt = datetime.fromisoformat(clean_dt)
                else:
                    dt = deadline
                time_left_hours = (dt - now).total_seconds() / 3600.0
                time_left_str = f"{time_left_hours:.1f} hours"
            except Exception as ex:
                logger.warning(f"Error computing time left: {ex}")

        missions = getattr(task, 'missions', task.get('missions') if isinstance(task, dict) else [])
        total_missions = len(missions)
        completed_missions = sum(1 for m in missions if getattr(m, 'is_completed', m.get('is_completed') if isinstance(m, dict) else False))
        progress_pct = (completed_missions / total_missions) * 100.0 if total_missions > 0 else 0

        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Perform an Atlas Assessment on the timeline execution:
Task: {title}
Description: {description}
Time Left: {time_left_str}
Progress: Completed {completed_missions}/{total_missions} missions ({progress_pct:.1f}%)

Return ONLY a JSON object with:
- "risk_score": integer (0 to 100) representing timeline execution risk
- "completion_probability": integer (0 to 100) representing completion chance
- "reason": detailed yet concise explanation reasoning about why this risk score and completion probability were assigned based on the deadline, remaining time, and progress. Your tone must be that of a professional and calm productivity coach. Explain your calculation and reasoning thoroughly.
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
            safe_print("[Gemini] Using Fallback")
            return self._analyze_risk_fallback(time_left_hours, completed_missions, total_missions)

    def generate_rescue_plan(self, task):
        """
        Generates a 3-step action recovery plan for high-risk goals.
        Returns:
        {
         "plan": "..."
        }
        """
        title = getattr(task, 'title', task.get('title') if isinstance(task, dict) else '')
        description = getattr(task, 'description', task.get('description') if isinstance(task, dict) else '')
        missions = getattr(task, 'missions', task.get('missions') if isinstance(task, dict) else [])
        
        incomplete_missions_list = [
            (m.title if hasattr(m, 'title') else m.get('title'))
            for m in missions
            if not (m.is_completed if hasattr(m, 'is_completed') else m.get('is_completed', False))
        ]
        incomplete_str = "\n".join([f"- {m}" for m in incomplete_missions_list])

        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Create an accelerated, highly specific, and actionable Atlas Recovery Strategy for:
Goal: {title}
Description: {description}
Remaining Missions:
{incomplete_str}

Return ONLY a JSON object with:
- "plan": a string containing a professional 3-step recovery checklist to save this objective. The steps must be highly actionable, specific to the remaining missions of this task, and avoid generic advice. Following this sequence maximizes your completion probability.
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
            safe_print("[Gemini] Using Fallback")
            return self._generate_rescue_plan_fallback(title, incomplete_missions_list)

    def generate_daily_brief(self, task_title, task_desc, missions, priority, risk_score, completion_prob, days_remaining):
        """
        Generates a personalized daily briefing.
        """
        missions_summary = [{"title": m.get("title"), "is_completed": m.get("is_completed")} for m in missions]
        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Generate an Atlas Briefing for the user based on their current quest data:
Quest Title: {task_title}
Description: {task_desc}
Missions: {json.dumps(missions_summary)}
Priority Score: {priority}/100
Risk / Assessment Score: {risk_score}/100
Completion Probability: {completion_prob:.2f}
Days Remaining: {days_remaining}

Your tone should be professional, calm, concise, and encouraging. Never be overly casual or robotic. Avoid emojis.

Return ONLY a JSON object matching this schema:
{{
  "headline": "Briefing headline (<10 words)",
  "summary": "Briefing summary (<40 words)",
  "today_focus": "The primary focus for today (<20 words)",
  "warning": "Optional timeline warning or assessment alert (can be empty string)",
  "motivation": "One sentence of motivational coaching"
}}

Constraints:
- "headline" must be less than 10 words.
- "summary" must be less than 40 words.
- "today_focus" must be less than 20 words.
- "motivation" must be exactly one sentence.
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
            safe_print("[Gemini] Using Fallback")
            return self._fallback_daily_brief(task_title)

    def generate_todays_mission(self, task_title, task_desc, missions):
        """
        Determines the single highest-impact active/incomplete mission to focus on today.
        """
        missions_summary = [{"title": m.get("title"), "is_completed": m.get("is_completed"), "is_unlocked": m.get("is_unlocked")} for m in missions]
        prompt = f"""
Act as Atlas, an elite AI executive productivity coach. Out of the following missions for the quest '{task_title}' (description: {task_desc}), determine the ONE single highest-impact active (unlocked and incomplete) mission to focus on today (Atlas Focus).

Missions list:
{json.dumps(missions_summary)}

Return ONLY a JSON object matching this schema:
{{
  "title": "Mission Title (must match one of the active/incomplete missions exactly)",
  "reason": "Why this mission is the highest impact today (must convey: 'Based on your current progress, completing this mission today provides the greatest impact.')",
  "estimated_time": "Estimated duration (e.g. '45 minutes')",
  "benefit": "Expected completion benefit"
}}
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
            safe_print("[Gemini] Using Fallback")
            return self._fallback_todays_mission(missions)

    def _fallback_daily_brief(self, task_title):
        return {
            "headline": f"Atlas Briefing: {task_title}",
            "summary": "Consistent execution of active milestones is recommended to secure the deadline.",
            "today_focus": "Complete the active mission.",
            "warning": "Deadline risk has increased. I recommend shifting your focus to the active mission.",
            "motivation": "Your plan is set. Proceed with calm and steady focus."
        }

    def _fallback_todays_mission(self, missions):
        active = "Complete active milestone"
        for m in missions:
            is_completed = m.get('is_completed', False) if isinstance(m, dict) else getattr(m, 'is_completed', False)
            if not is_completed:
                active = m.get('title', active) if isinstance(m, dict) else getattr(m, 'title', active)
                break
        return {
            "title": active,
            "reason": "Based on your current progress, completing this mission today provides the greatest impact.",
            "estimated_time": "60 minutes",
            "benefit": "Unlocks the next chronological stage of the quest."
        }


    def _generate_missions_fallback(self, goal):
        cleaned_goal = goal.lower()
        if "paper" in cleaned_goal or "research" in cleaned_goal:
            return [
                {"title": "Search Google Scholar for 3-5 key papers and summarize key findings", "order": 1},
                {"title": "Identify clear research gaps and write down the core hypothesis", "order": 2},
                {"title": "Draft the methodology section and list necessary experiment steps", "order": 3},
                {"title": "Write the introduction and background review sections", "order": 4},
                {"title": "Complete final editing, formatting, and citation checks", "order": 5}
            ]
        elif "code" in cleaned_goal or "build" in cleaned_goal or "app" in cleaned_goal or "project" in cleaned_goal:
            return [
                {"title": "Design application architecture and structure codebase", "order": 1},
                {"title": "Implement core backend models, endpoints, and database connection", "order": 2},
                {"title": "Build frontend pages, responsive layout, and API service connection", "order": 3},
                {"title": "Execute end-to-end integration and run validation tests", "order": 4},
                {"title": "Deploy MVP, apply styling upgrades, and final bug fixing", "order": 5}
            ]
        else:
            return [
                {"title": f"Plan strategy and define outline for {goal}", "order": 1},
                {"title": "Gather required assets, references, and toolsets", "order": 2},
                {"title": "Implement first core step and review outcome details", "order": 3},
                {"title": "Refine secondary components and integrate all workflows", "order": 4},
                {"title": "Do final pass verification and mark the objective complete", "order": 5}
            ]

    def _analyze_risk_fallback(self, time_left_hours, completed, total):
        progress = completed / total if total > 0 else 0
        if time_left_hours <= 0:
            return {
                "risk_score": 100,
                "completion_probability": 0,
                "reason": "The target deadline has already passed. Timeline execution has ceased."
            }
        
        prob = min(1.0, max(0.0, progress + (time_left_hours / 100.0) * 0.5))
        risk = int((1.0 - prob) * 100)
        
        if prob < 0.4:
            reason = f"Timeline parameters are critically tight. Only {completed}/{total} missions complete. I recommend prioritizing the immediate milestone."
        elif prob < 0.75:
            reason = f"Moderate timeline deficit detected. Completed {completed}/{total} missions. Focus must be maintained to prevent bottlenecks."
        else:
            reason = f"Timeline metrics appear stable. Completed {completed}/{total} missions. Execution is on track."

        return {
            "risk_score": risk,
            "completion_probability": int(prob * 100),
            "reason": reason
        }

    def _generate_rescue_plan_fallback(self, title, incomplete_list):
        step_one = f"Resolve the immediate bottleneck: {incomplete_list[0] if incomplete_list else 'remaining list'}."
        return {
            "plan": f"1. Scope optimization: Focus exclusively on core requirements.\n2. Targeted sprint: Work on '{step_one}' in a dedicated block.\n3. Postpone secondary details until the core trajectory is secure."
        }
