import json
import os
import sys
import webbrowser

import requests
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件

# 读取环境变量
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME", "rehui_api")
token = os.getenv("GITHUB_TOKEN")

def initialize_git():
    print("🔧 初始化 Git 仓库 ...")
    subprocess.run(["git", "init"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "🎉 init rehui_api project"])

def create_repo_if_not_exists(token):
    print(f"🔍 检查 GitHub 是否已存在仓库 {REPO_NAME} ...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    check_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"
    res = requests.get(check_url, headers=headers)

    if res.status_code == 200:
        print("✅ 仓库已存在，跳过创建步骤。")
    else:
        print("📁 仓库不存在，准备自动创建...")
        data = {"name": REPO_NAME, "private": False, "auto_init": False}
        create_res = requests.post("https://api.github.com/user/repos", headers=headers, data=json.dumps(data))

        if create_res.status_code == 201:
            print("✅ 仓库创建成功！")
        else:
            print("❌ 仓库创建失败：", create_res.text)
            sys.exit(1)

def push_to_github():
    print("🚀 推送代码到 GitHub ...")
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    remote_result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if "origin" not in remote_result.stdout:
        subprocess.run(["git", "remote", "add", "origin", remote_url])

    subprocess.run(["git", "branch", "-M", "main"])
    result = subprocess.run(["git", "push", "-u", "origin", "main", "--force"])
    if result.returncode == 0:
        print("✅ 推送成功！")
    else:
        print("❌ 推送失败，请检查 GitHub 返回的错误")

def open_render_page():
    print("🌍 打开 Render 部署页面 ...")
    webbrowser.open("https://dashboard.render.com/new/web")
    print("✅ 完成！点击仓库一键部署 rehui_api 即可 🎉")

import subprocess

def remove_from_github_only(paths):
    """
    只从 GitHub 上删除指定文件或目录，不删除本地数据
    :param paths: 要删除的路径列表，例如 ["scripts", "README.md"]
    """
    for path in paths:
        print(f"🧹 从 Git 控制中移除: {path}")
        result = subprocess.run(["git", "rm", "--cached", "-r", path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ 失败: {path}")
            print(result.stderr)
        else:
            print(f"✅ 成功标记移除: {path}")

    subprocess.run(["git", "commit", "-m", "🔥 remove files from GitHub only"], check=False)
    subprocess.run(["git", "push"], check=True)
    print("🚀 推送完成，GitHub 上对应文件已删除（本地文件仍保留）")


# def open_render_deploy_page():
#     print("🌐 打开 Render 部署页面 ...")
#     url = f"https://render.com/deploy?repo=https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
#     webbrowser.open(url)

if __name__ == "__main__":

    initialize_git()
    # create_repo_if_not_exists(token)
    # remove_from_github_only([".idea"])
    push_to_github()

    # open_render_page()
    # open_render_deploy_page()
