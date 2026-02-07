import os
import json
import re
import sys
from google import genai

# 1. Load Data
try:
    with open("jira_db.json", "r") as f:
        jira_db = json.load(f)
    with open("RELEASE_NOTES.md", "r") as f:
        notes_content = f.read()
except FileNotFoundError:
    print("❌ Critical Files Missing.")
    sys.exit(1)

# 2. Extract Tickets from Notes
mentioned_tickets = re.findall(r"(JIRA-\d+)", notes_content)
blocked_tickets = []

print("🔍 Analyzing Release Candidate...")

# 3. Find Blockers
for ticket in mentioned_tickets:
    info = jira_db.get(ticket)
    if info and info['status'] != "Closed":
        blocked_tickets.append(f"{ticket} ({info['status']}): {info['summary']}")

if not blocked_tickets:
    print("✅ All tickets are closed. Release Approved.")
    sys.exit(0)

# 4. AI Risk Analysis
print(f"⚠️ Found {len(blocked_tickets)} blocked tickets. engaging Risk Analyst AI...")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
prompt = f"""
You are a Senior Technical Project Manager.
The release is blocked because the following tickets are listed in the Release Notes but are NOT Closed in Jira.

BLOCKED TICKETS:
{json.dumps(blocked_tickets, indent=2)}

YOUR TASK:
For each blocked ticket, provide a "Risk Assessment":
1. **Analyze the Root Cause**: Based strictly on the summary, guess why it might be stuck (e.g., "Payment Gateway" -> likely compliance or API key issues).
2. **Resource Prediction**: What specific role is needed to unblock this? (e.g., Senior Backend Engineer, DBA, Legal).
3. **Impact**: If we ship without this, what is the risk?

Format the output as a clean Markdown report.
"""

response = client.models.generate_content(
    model="gemini-2.0-flash-lite-001",
    contents=prompt
)

# 5. Output the Report and Fail the Pipeline
report_file = "BLOCKER_ANALYSIS.md"
with open(report_file, "w") as f:
    f.write(f"# 🚨 Release Governance Blocked\n\n")
    f.write(response.text)

print(f"\n❌ Release Blocked. Analysis saved to {report_file}")
print(response.text)
sys.exit(1) # Fail the pipeline