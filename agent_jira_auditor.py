import os
import json
import re
import sys

# 1. Load the "Mock Jira" Database
try:
    with open("jira_db.json", "r") as f:
        jira_db = json.load(f)
except FileNotFoundError:
    print("❌ Error: jira_db.json not found.")
    sys.exit(1)

# 2. Read the Release Notes
try:
    with open("RELEASE_NOTES.md", "r") as f:
        notes_content = f.read()
except FileNotFoundError:
    print("❌ Error: RELEASE_NOTES.md not found. Did Agent 1 run?")
    sys.exit(1)

print("🔍 Auditing Release Notes against Jira Database...")

# 3. Extract Ticket Numbers using Regex (Matches JIRA-XXX)
mentioned_tickets = re.findall(r"(JIRA-\d+)", notes_content)
unique_tickets = set(mentioned_tickets)

if not unique_tickets:
    print("⚠️ Warning: No Jira tickets found in release notes.")
    # In strict mode, we might want to fail here, but let's pass for now
    sys.exit(0)

# 4. Verify Status of Each Ticket
errors = []

for ticket in unique_tickets:
    ticket_info = jira_db.get(ticket)
    
    if not ticket_info:
        errors.append(f"❌ {ticket}: Ticket does not exist in Jira System.")
        continue

    status = ticket_info['status']
    print(f"checking {ticket}... Status: {status}")

    if status != "Closed":
        errors.append(f"⛔ {ticket}: Ticket is '{status}' but listed in Release Notes. It must be 'Closed'.")

# 5. Final Verdict
if errors:
    print("\n🚨 AUDIT FAILED:")
    for e in errors:
        print(e)
    sys.exit(1) # Kill the pipeline
else:
    print("\n✅ AUDIT PASSED: All tickets are valid and closed.")
    sys.exit(0)