import os, sys

from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

USER_FILE = BASE_DIR / ".env.user"
if USER_FILE.exists():
    load_dotenv(USER_FILE, override=True)

class Settings(BaseSettings):
    github_owner: str = ''
    github_repo: str = ''
    
    github_repo_token: str = ''
    gist_token: str = ''

settings = Settings()

if __name__ == "__main__":
    print(settings.model_dump())
    
