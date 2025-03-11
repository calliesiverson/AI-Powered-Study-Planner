import os
import google.generativeai as genai

# Load API key from environment variable
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
    if not existing_tasks:
        task_info = "There are no existing tasks. Create a fresh study plan for this new task."
    else:
        task_info = f"Consider these existing tasks: {existing_tasks}"

    prompt = f"""
    Generate a detailed study plan for the task: {task_title}.
    {task_info}
    The plan should include recommended study times, important topics to cover, and break periods.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        print("✅ API Response:", response.text)  # Print response to debug
        return response.text
    
    except Exception as e:
        print("❌ Error:", str(e))
        return "Error generating study plan"
