import streamlit as st
import os
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# OpenRouter API Key
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Jira credentials
domain = os.getenv("JIRA_DOMAIN")
project = os.getenv("JIRA_PROJECT")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")

# Jira API config
url = f"https://{domain}/rest/api/3/search"
auth = (email, api_token)
headers = {"Accept": "application/json"}

# Fetch Done epics from Jira
def fetch_completed_epics():
    jql = f"project={project} AND issuetype=Epic AND status=Done"
    response = requests.get(url, headers=headers, auth=auth, params={"jql": jql})
    response.raise_for_status()
    return response.json().get("issues", [])

# Generate LinkedIn post using OpenRouter
def generate_ai_post(epic):
    title = epic["fields"]["summary"]
    reporter = epic["fields"]["reporter"]["displayName"]
    description = ""
    for block in epic["fields"].get("description", {}).get("content", []):
        for content in block.get("content", []):
            if content["type"] == "text":
                description += content["text"] + " "

    prompt = f"""
You are a professional content creator for LinkedIn. Write a concise, engaging post that reflects a milestone achieved in a software team based on the following epic:


Title: {title}
Reporter: {reporter}
Description: {description}

Write it as a personal team announcement with a professional tone and a touch of enthusiasm.
Give It In A  Unique and refreshing manner rather than same and standred format for a linkedin post
"""

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "your-app-name",
    }

    data = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# Save post to .txt file with status
def save_post_to_file(content, status="approved"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6]
    filename = f"{status}_post_{timestamp}_{uid}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content.strip())

# Streamlit UI
st.title("📢 AI-Generated Jira Epic LinkedIn Posts")

try:
    epics = fetch_completed_epics()
    if not epics:
        st.info("No completed epics found.")
    else:
        for i, epic in enumerate(epics):
            ai_post = generate_ai_post(epic)
            with st.expander(f"📌 Epic {i+1}: {epic['fields']['summary']}"):
                edited = st.text_area("✏️ Review or Edit the post:", ai_post, key=i, height=200)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{i}"):
                        save_post_to_file(edited, status="approved")
                        st.success("Post approved and saved.")
                with col2:
                    if st.button("🗑️ Skip", key=f"skip_{i}"):
                        st.warning("Post skipped.")
                with col3:
                    if st.button("💾 Save Draft", key=f"draft_{i}"):
                        save_post_to_file(edited, status="draft")
                        st.info("Post saved as draft.")
except Exception as e:
    st.error(f"⚠️ Error: {str(e)}")
