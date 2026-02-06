import os
import sys
from google import genai

# 1. Get the Commit Message from the Environment
commit_message = os.environ.get("COMMIT_MESSAGE", "No message provided")
print(f"🔍 Analyzing commit: '{commit_message}'")

# 2. Connect to Gemini (Key comes from GitHub Secrets)
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 3. Ask the "Gatekeeper" Question
    prompt = f"""
    You are a Release Governance Bot.
    Analyze this commit message: "{commit_message}"
    
    Rules:
    1. It must be descriptive (more than 2 words).
    2. It must not contain profanity.
    3. It should sound professional.
    
    Reply with ONLY the word "PASS" or "FAIL", followed by a short reason.
    Example: FAIL: Too vague.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents=prompt
    )
    result = response.text.strip()
    print(f"🤖 AI Verdict: {result}")

    # 4. Enforce the Decision
    if result.startswith("PASS"):
        print("✅ Release Approved.")
        sys.exit(0)  # Success exit code
    else:
        print("❌ Release Blocked by Governance Policy.")
        sys.exit(1)  # Failure exit code (Kills the pipeline)

except Exception as e:
    print(f"Error calling AI: {e}")
    sys.exit(1) # Fail safe