import shutil
import subprocess
import sys
from pathlib import Path

GITHUB_USERNAME = "zhizhunbao"
REPO_NAME = "rehui_api"

def install_dependencies():
    print("📦 安装依赖 fastapi + uvicorn + python-dotenv ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "python-dotenv", "git-filter-repo"])

def create_project_structure(project_dir: Path):
    api_dir = project_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    (api_dir / "main_api.py").write_text('''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"msg": "pong"}

@app.get("/api/rank/top")
def get_top_rank():
    return {"top": ["Car A", "Car B", "Car C"]}
''')

    (project_dir / "start_render.py").write_text('''\
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main_weapp_api:app", host="0.0.0.0", port=8000)
''')

    (project_dir / "requirements.txt").write_text('''\
fastapi
uvicorn
python-dotenv
sqlalchemy
pandas
psycopg2
''')

    (project_dir / "render.yaml").write_text('''\
services:
  - type: web
    name: rehui_api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python start_render.py
    plan: free
    branch: main
    autoDeploy: true
''')

    (project_dir / ".gitignore").write_text('''\
__pycache__/
*.pyc
.env
.idea/
.venv/
.idea/
db/
''')

    print("✅ 项目结构已创建。")

def main():
    project_dir = Path(".")
    install_dependencies()
    create_project_structure(project_dir)

if __name__ == "__main__":
    main()
