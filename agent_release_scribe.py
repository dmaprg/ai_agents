import os
import subprocess
from google import genai

# 1. Get the last 5 commits from Git
# We use git log to get the raw raw data
raw_commits = subprocess.check_output(
    ["git", "log", "-5", "--pretty=format:%h - %s"], 
    encoding="utf-8"
)

print("📝 Raw Commits found:")
print(raw_commits)

# 2. Ask AI to write the Release Notes
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
You are a Technical Writer. 
Convert these raw git commit logs into a clean "RELEASE_NOTES.md" format.

RAW LOGS:
{raw_commits}

RULES:
1. Group items into "🚀 Features" and "🐛 Bug Fixes".
2. For every item, ensure the JIRA-ID is clearly listed (e.g., [JIRA-101]).
3. Do not include 'merge' commits.
4. Output strictly the Markdown content.
"""

response = client.models.generate_content(
    model="gemini-2.0-flash-lite-001",
    contents=prompt
)

# 3. Save the file
with open("RELEASE_NOTES.md", "w") as f:
    f.write(response.text)

print("\n✅ RELEASE_NOTES.md generated successfully!")
print(response.text)