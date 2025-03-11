import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load API key from environment variable
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY is missing! Make sure it's set in your environment.")
else:
    print("✅ GEMINI_API_KEY loaded successfully.")

# Configure the Gemini API
genai.configure(api_key=api_key)

def generate_study_plan(task_title, existing_tasks):
    print("📌 Generating study plan for:", task_title)

    # Handle case where there are no existing tasks
    task_info = "There are no existing tasks. Create a fresh study plan for this new task." if not existing_tasks else f"Consider these existing tasks: {existing_tasks}"

    prompt = f"""
    You are an AI study planner. Generate a detailed study plan as a **strictly formatted JSON object**.
    
    Task: "{task_title}"
    {task_info}

    Return JSON with the following fields:
    {{
        "goal": "string",
        "time_commitment": "string",
        "recommended_resources": {{
            "books": ["list of book titles"],
            "websites": ["list of website names"],
            "videos": ["list of video resources"]
        }},
        "weekly_breakdown": [ ## Note: add more weeks as needed
            {{"week": 1, "topics": ["topic 1", "topic 2"]}},
            {{"week": 2, "topics": ["topic 3", "topic 4"]}}
        ],
        "daily_breakdown": [
            {{"day": 1, "study_time": "2 hours", "topics": ["topic A", "topic B"], "breaks": ["break details"]}}
        ],  ## Note: add days 2-7 * each week included in the weekly breakdown
        "tips": ["list of success tips"]
    }}

    **Output only valid JSON. Do not include any additional text.**
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash",
                                      generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)

        print("✅ Raw API Response:", response.text)  # Debugging

        # Ensure response is in JSON format
        try:
            study_plan = json.loads(response.text)  # Convert AI response to Python dictionary
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON: {e}")
            return {"error": "Invalid JSON response from AI."}

        # Normalize missing sections with defaults
        study_plan = {
            "task": task_title,
            "goal": study_plan.get("goal", "No goal provided."),
            "time_commitment": study_plan.get("time_commitment", "No time commitment specified."),
            "recommended_resources": study_plan.get("recommended_resources", {"books": [], "websites": [], "videos": []}),
            "weekly_breakdown": study_plan.get("weekly_breakdown", []),
            "daily_breakdown": study_plan.get("daily_breakdown", []),
            "tips": study_plan.get("tips", []),
        }

        print("✅ Processed Study Plan:", study_plan)  # Debugging
        return study_plan

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return {"error": "Failed to generate study plan."}
