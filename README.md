# OJP Issue Intake

This is a small FastAPI service that acts as a front door to the [OpenTdataCH OJP](https://github.com/openTdataCH/ojp-sdk) GitHub ecosystem: it collects issue reports through a web form/API and automatically creates, enriches, and places GitHub issues into the correct project board.

## Install

```
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

## Configure

Edit `.env` or create and edit `.env.user` (.git ignored)

| ENV var | ex value | comments |
| - | - | - |
| `GITHUB_OWNER` | `openTdataCH` | Github user/org under which the issues are created |
| `GITHUB_REPO` | `ojp-sdk` | Github repo under which the issues are created |
| `GITHUB_REPO_TOKEN` | `github_pat_11AAA32SQ0fv7VoqGc ...` | Github PAT with write access for repo/user above |
| `GIST_TOKEN` | `ghp_R8R2aGD ...` | gist.github.com token where the XML gists are created |

## Run Server

```
# in ./src
$ uvicorn server:app --host 0.0.0.0 --port 8000
```

## Example

```
POST /ojp_sdk_issue

Payload JSON
{
  "title": "string",
  "description": "string",
  "requestXML": "string",
  "responseXML": "string",
  "projectKey": "string"
}
```

where

| field | type | required | description |
| - | - | - | - |
| `title` | `string` | `yes` | title of the Github issue that will be created |
| `description` | `string` | `yes` | description of the Github issue that will be created |
| `requestXML` | `string` | `yes` | OJP XML request |
| `responseXML` | `string` | `yes` | OJP XML response |
| `projectKey` | `string` | `yes` | project key, see MAP_PROJECT_IDS in [./src/server.py](./src/server.py) for the actual mapping id to Github projects |
