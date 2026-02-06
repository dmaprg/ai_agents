import os
import sys
import datetime
from google import genai

# 1. Get the Commit Message & Current Day
commit_message = os.environ.get("COMMIT_MESSAGE", "No message provided")
current_day = datetime.datetime.now().strftime("%A")

print(f"🔍 Analyzing commit: '{commit_message}'")
print(f"📅 Current Day: {current_day}")

# 2. Load the Policy as Code
try:
    with open("release_policy.md", "r") as f:
        policy_content = f.read()
    print("📜 Policy loaded successfully.")
except FileNotFoundError:
    print("❌ Critical Error: release_policy.md not found!")
    sys.exit(1)

# 3. Connect to Gemini
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 4. The Dynamic Prompt
    prompt = f"""
    You are a Release Governance Officer.
    
    CONTEXT:
    - Today is: {current_day}
    - Commit Message: "{commit_message}"
    
    YOUR INSTRUCTIONS:
    Analyze the commit message strictly against the following POLICY rules.
    If ANY rule is violated, you must FAIL the release.
    
    === POLICY START ===
    {policy_content}
    === POLICY END ===
    
    OUTPUT FORMAT:
    Reply with ONLY the word "PASS" or "FAIL", followed by the specific rule violated (if any).
    Example: FAIL: Missing Ticket ID.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents=prompt
    )
    result = response.text.strip()
    print(f"🤖 AI Verdict: {result}")

    if result.startswith("PASS"):
        print("✅ Release Approved.")
        sys.exit(0)
    else:
        print("❌ Release Blocked by Governance Policy.")
        sys.exit(1)

except Exception as e:
    print(f"Error calling AI: {e}")
    sys.exit(1)