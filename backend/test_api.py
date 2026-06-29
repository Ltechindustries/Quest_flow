import time
import requests
import sys

BASE_URL = "http://localhost:5000"

def run_tests():
    print("Starting backend API tests...")
    
    # 1. Health Check
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health Check: Code {response.status_code}, Response: {response.json()}")
        if response.status_code != 200:
            print("Health check failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        sys.exit(1)

    # 2. Create Task (Normal timeline)
    print("\n--- Creating a normal task ---")
    deadline_normal = "2026-06-30T12:00:00"  # About 7 days from now
    payload_normal = {
        "title": "Build a Flask Backend MVP",
        "description": "Create SQLite models, write Flask routers, connect to Gemini, and write tests.",
        "deadline": deadline_normal
    }
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload_normal)
    print(f"Create Task: Code {response.status_code}")
    if response.status_code != 201:
        print(f"Failed: {response.text}")
        sys.exit(1)
    
    task_data = response.json()
    task_id = task_data['id']
    missions = task_data['missions']
    print(f"Created Task ID: {task_id}")
    print(f"Priority Score: {task_data['priority_score']}, Risk Level: {task_data['risk_level']}")
    print(f"Missions returned: {len(missions)}")
    for m in missions:
        print(f"  - Mission: '{m['title']}' | Order: {m['order_index']} | Unlocked: {m['is_unlocked']} | Completed: {m['is_completed']}")

    # Check if first mission is unlocked and others locked
    if not missions[0]['is_unlocked']:
        print("Error: First mission should be unlocked!")
        sys.exit(1)
    for m in missions[1:]:
        if m['is_unlocked']:
            print("Error: Subsequent missions should be locked initially!")
            sys.exit(1)

    # 3. Create Task (High risk timeline - past/short deadline)
    print("\n--- Creating an urgent/overdue task (should trigger High Risk and Rescue Plan) ---")
    deadline_urgent = "2026-06-23T20:00:00"  # Very soon
    payload_urgent = {
        "title": "Emergency Server Deployment",
        "description": "Fix production crash immediately.",
        "deadline": deadline_urgent
    }
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload_urgent)
    print(f"Create Urgent Task: Code {response.status_code}")
    if response.status_code != 201:
        print(f"Failed: {response.text}")
        sys.exit(1)
    
    urgent_task = response.json()
    print(f"Urgent Task Risk Level: {urgent_task['risk_level']}")
    print(f"Risk Score: {urgent_task['risk_score']}, Completion Prob: {urgent_task['completion_probability']}")
    print(f"Rescue Plan: {urgent_task['rescue_plan']}")
    
    if urgent_task['risk_level'] != "High":
        print("Warning: Expected High Risk level for very short deadline, but got:", urgent_task['risk_level'])
    if not urgent_task['rescue_plan']:
        print("Warning: Expected Rescue Plan for High Risk, but got None/Empty.")

    # 4. Complete first mission of normal task
    print("\n--- Completing the first mission ---")
    first_mission_id = missions[0]['id']
    response = requests.post(f"{BASE_URL}/api/missions/{first_mission_id}/complete")
    print(f"Complete Mission {first_mission_id}: Code {response.status_code}")
    if response.status_code != 200:
        print(f"Failed: {response.text}")
        sys.exit(1)

    updated_task = response.json()
    updated_missions = updated_task['missions']
    print("Missions after completion:")
    for m in updated_missions:
        print(f"  - Mission: '{m['title']}' | Order: {m['order_index']} | Unlocked: {m['is_unlocked']} | Completed: {m['is_completed']}")

    # First mission should be complete, second unlocked
    if not updated_missions[0]['is_completed']:
        print("Error: First mission should be completed!")
        sys.exit(1)
    if not updated_missions[1]['is_unlocked']:
        print("Error: Second mission should now be unlocked!")
        sys.exit(1)

    print("\n--- Deleting urgent task ---")
    del_response = requests.delete(f"{BASE_URL}/api/tasks/{urgent_task['id']}")
    print(f"Delete Task: Code {del_response.status_code}")

    print("\nAll backend integration tests completed successfully!")

if __name__ == "__main__":
    run_tests()
