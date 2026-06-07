import os, sys

from datetime import datetime
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings

app = FastAPI(title="GitHub Ticket API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_OWNER = settings.github_owner
GITHUB_REPO = settings.github_repo
print('=' * 20)
print(f'Github-Issues Server')
print('=' * 20)
print(f'github_owner: {GITHUB_OWNER}')
print(f'github_repo: {GITHUB_REPO}')
print()

MAP_PROJECT_IDS = {
    # https://github.com/orgs/openTdataCH/projects/11/views/1
    "ojp2_backend_issues": "PVT_kwDOAXGusc4AhSBn",
    # https://github.com/orgs/openTdataCH/projects/10/views/1
    "ojp2_sdks": "PVT_kwDOAXGusc4AeVtd",
    # https://github.com/orgs/openTdataCH/projects/5/views/1
    "ojp_siri_sx_current": "PVT_kwDOAXGusc4AMjtn",
}

class Ticket(BaseModel):
    title: str
    description: str
    requestXML: str
    responseXML: str
    projectKey: str

# ── helpers ────────────────────────────────────────────────────
def create_gist(name: str, xml: str) -> str:
    request_headers = {
        "Authorization": f"token {settings.gist_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    r = requests.post(
        "https://api.github.com/gists",
        headers=request_headers,
        json={
            "description": f"Diagnostics – {name}",
            "public": False,
            "files": { name: { "content": xml } }
        },
        timeout=10,
    )
    if r.status_code != 201:
        raise HTTPException(500, f"Gist error: {r.text}")
    return r.json()["html_url"]

def create_issue(title: str, body: str):
    request_headers = {
        "Authorization": f"token {settings.github_repo_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    r = requests.post(
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues",
        headers=request_headers,
        json={ "title": title, "body": body },
        timeout=10,
    )
    if r.status_code != 201:
        raise HTTPException(500, f"Issue error: {r.text}")
    return r.json()

def assign_ticket_project(content_id: str, project_id: str):
    gq_query = """
mutation AddToProject($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {
    projectId: $projectId,
    contentId: $contentId
  }) {
    item { id }
  }
}
"""
    gq_vars = {"projectId": project_id, "contentId": content_id}
    
    request_headers = {
        "Authorization": f"Bearer {settings.github_repo_token}",
        "Accept": "application/json",
    }
    
    requests.post(
        "https://api.github.com/graphql",
        headers=request_headers,
        json={"query": gq_query, "variables": gq_vars},
        timeout=10,
    )

# ── endpoint ──────────────────────────────────────────────────
@app.post("/ojp_sdk_issue")
def open_ticket(t: Ticket):
    request_ts_f = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    
    request_gist_url = create_gist(f'{request_ts_f}-request.xml',  t.requestXML)
    response_gist_url = create_gist(f'{request_ts_f}-response.xml',  t.responseXML)

    body = (
        f"{t.description}\n\n"
        "----\n\n"
        "OJP Request/Response XML:\n"
        f"- [request.xml]({request_gist_url})\n"
        f"- [response.xml]({response_gist_url})\n\n"
        "Issue generated with ojp-issue-intake"
    )

    issue = create_issue(t.title, body)
    issue_url = issue["html_url"]
    
    node_id = issue["node_id"]
    project_id = MAP_PROJECT_IDS[t.projectKey]
    if project_id is None:
        raise HTTPException(400, f'Unknown projectKey: {t.projectKey}')

    assign_ticket_project(node_id, project_id)

    return { "issue_url": issue_url, "gists": [request_gist_url, response_gist_url] }
