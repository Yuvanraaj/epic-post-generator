import os
import requests
from dotenv import load_dotenv

load_dotenv()

domain = os.getenv("JIRA_DOMAIN")
project = os.getenv("JIRA_PROJECT")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")

if not domain:
    raise ValueError("JIRA_DOMAIN is missing!")

url = f"https://{domain}/rest/api/3/search"
auth = (email, api_token)
headers = {"Accept": "application/json"}

def fetch_completed_epics():
    jql = f"project={project} AND issuetype=Epic AND status=Done"
    response = requests.get(url, headers=headers, auth=auth, params={"jql": jql})
    response.raise_for_status()
    data = response.json()
    return data.get("issues", [])

def generate_summary(epic):
    fields = epic["fields"]
    title = fields["summary"]
    description = fields.get("description", {}).get("content", [])
    description_text = ""

    if description:
        for block in description:
            if block["type"] == "paragraph":
                for content in block.get("content", []):
                    if content["type"] == "text":
                        description_text += content["text"] + " "

    status = fields["status"]["name"]
    created = fields["created"]
    reporter = fields["reporter"]["displayName"]

    return f"""
📌 Epic Summary
- Title: {title}
- Status: {status}
- Created: {created}
- Reporter: {reporter}
- Description: {description_text.strip()}
""".strip()

def generate_linkedin_post(epic):
    summary = generate_summary(epic)
    title = epic["fields"]["summary"]
    industry_context = "In today's dynamic tech landscape, tracking and delivering outcomes with focus is essential."

    return f"""
🚀 Epic Completed: "{title}"

{industry_context}

🔍 Highlights:
{summary}

#Agile #ProjectManagement #Jira #SoftwareDevelopment
""".strip()

def approval_flow(post):
    print("\n" + "="*60)
    print("📝 Draft LinkedIn Post:\n")
    print(post)
    print("\n" + "="*60)
    return input("✅ Approve this post? (yes/no/edit): ").strip().lower()

def save_post_to_file(post, filename="approved_posts.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(post + "\n\n" + "="*80 + "\n\n")
    print(f"✅ Post saved to '{filename}'")

# 🔄 Main Execution Flow
epics = fetch_completed_epics()

for epic in epics:
    post = generate_linkedin_post(epic)
    decision = approval_flow(post)

    if decision == "yes":
        save_post_to_file(post)
    elif decision == "edit":
        print("✏️ Enter your edited post below (end with an empty line):")
        edited_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            edited_lines.append(line)
        edited_post = "\n".join(edited_lines)
        if input("✅ Approve edited post? (yes/no): ").strip().lower() == "yes":
            save_post_to_file(edited_post)
    else:
        print("❌ Post skipped.\n")
