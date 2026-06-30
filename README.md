# 🚀 QuestFlow AI – Atlas Executive Productivity Coach

> Transform ambitious goals into structured missions with AI-powered planning, adaptive coaching, and intelligent execution.

---

## 📌 Overview

QuestFlow AI is an intelligent productivity platform that helps users convert large, overwhelming goals into manageable, sequential missions.

Powered by **Google Gemini**, QuestFlow AI acts as an executive productivity coach named **Atlas**, providing intelligent task decomposition, risk assessment, rescue strategies, and daily execution guidance.

Instead of simply tracking tasks, QuestFlow AI continuously analyzes progress and guides users toward successful completion.

---

## ✨ Key Features

### 🎯 AI Goal Decomposition
Convert a high-level goal into a structured sequence of actionable missions.

### 🔓 Progressive Mission Unlocking
Only the current mission is unlocked, helping users maintain focus and reduce overwhelm.

### 📊 Risk Analysis
Analyze deadline constraints and completion progress to estimate:

- Risk Score
- Completion Probability
- Risk Level

### 🛟 Rescue Strategy
When a project becomes high-risk, Atlas generates an intelligent recovery plan.

### 📅 Daily Brief
Receive an AI-generated daily summary highlighting:

- Today's priority
- Current risks
- Recommended focus
- Motivation

### 🧠 Atlas Executive Coach
Atlas provides intelligent recommendations throughout the project lifecycle to improve productivity.

### 📈 Progress Dashboard
Track mission completion, overall progress, and project health in real time.

---

# 🖥️ Demo

Live Application:

https://quest-flow-347055988735.asia-southeast1.run.app

---

# 🛠️ Tech Stack

## Frontend

- React
- Vite
- TypeScript
- Tailwind CSS v4
- Lucide React
- Motion

## Backend

- Flask
- SQLAlchemy
- SQLite
- Python

## AI

- Google Gemini API

## Deployment

- Google AI Studio
- Google Cloud Run

---

# 🏗️ Architecture

```
User Goal
      │
      ▼
 React Frontend
      │
 REST API
      │
      ▼
 Flask Backend
      │
      ├── Goal Decomposition
      ├── Risk Analysis
      ├── Rescue Strategy
      ├── Daily Brief
      └── Today's Mission
      │
      ▼
 Google Gemini API
      │
      ▼
 SQLite Database
      │
      ▼
 Dashboard
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/QuestFlow-AI.git
```

Navigate into the project

```bash
cd QuestFlow-AI
```

---

## Backend Setup

```bash
cd backend
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-2.5-flash

SECRET_KEY=questflow-secret
```

Run backend

```bash
python app.py
```

---

## Frontend Setup

```bash
npm install
```

Run

```bash
npm run dev
```

---

# 📂 Project Structure

```
QuestFlow-AI
│
├── backend
│   ├── routes
│   ├── services
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   └── requirements.txt
│
├── src
│   ├── components
│   ├── pages
│   ├── services
│   ├── types
│   ├── App.tsx
│   └── main.tsx
│
├── assets
├── public
└── package.json
```

---

# 🤖 How It Works

1. User creates a new Quest.
2. Atlas sends the goal to Gemini.
3. Gemini decomposes the goal into missions.
4. Risk is calculated.
5. Daily Brief is generated.
6. Rescue Strategy is generated when required.
7. User completes missions.
8. Progress updates automatically.

---

# 🌟 Highlights

- AI-powered task decomposition
- Executive coaching
- Adaptive productivity
- Progressive task unlocking
- Intelligent recovery planning
- Deadline-aware recommendations
- Modern responsive interface

---

# 🔮 Future Enhancements

- Calendar Integration
- Google Tasks Sync
- Team Collaboration
- Voice Assistant
- Email Notifications
- Mobile Application
- Analytics Dashboard
- Personalized AI Memory

---

# 🧪 Built With Google Technologies

- Google Gemini API
- Google AI Studio
- Google Cloud Run

---

# 👨‍💻 Developed By

**N. L. Lalith Raghavendra**

B.Tech Computer Science (AI & ML)

VIT Chennai

GitHub:
https://github.com/Ltechindustries

LinkedIn:
https://www.linkedin.com/in/lalith-raghavendra/

---

# 📄 License

This project was developed as part of a Hackathon submission and is released under the MIT License.

---

⭐ If you like this project, consider giving it a star!
