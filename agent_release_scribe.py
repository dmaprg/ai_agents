import os
import json
import sys
from google import genai

# 1. Idempotency Check (Don't overwrite if exists)
if os.path.exists("RELEASE_NOTES.md"):
    print("RELEASE_NOTES.md already exists. Skipping generation.")
    sys.exit(0)

# 2. Load Mock Jira Data
try:
    with open("jira_db.json", "r") as f:
        jira_data = json.load(f)
except FileNotFoundError:
    print("Error: jira_db.json not found.")
    sys.exit(1)

print("Generating Release Notes from Jira Data...")

# 3. Ask AI to Categorize and Format
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
You are a Release Manager. 
Convert this raw Jira JSON data into a clean "RELEASE_NOTES.md" file.

RAW DATA:
{json.dumps(jira_data, indent=2)}

RULES:
1. Categorize items into two sections: "New Features" and "Bug Fixes".
2. Use the "summary" field to decide the category (e.g., "Fix" = Bug, "Add/Implement" = Feature).
3. Format: - [TICKET_ID] Summary
4. Only include tickets that are relevant (ignore 'Open' or 'Backlog' if clearly not ready, but for this demo include ALL).
5. After inserting all tickets, place a Summary at the begining of the Release notes. the summary content should be from all the tickets but don't list each of them.
"""

response = client.models.generate_content(
    model="gemini-2.0-flash-lite-001",
    contents=prompt
)

# 4. Save the file
with open("RELEASE_NOTES.md", "w") as f:
    f.write(response.text)

print("\nRELEASE_NOTES.md generated successfully!")
print(response.text)