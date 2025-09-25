from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

approval_key = None
scheduler = BackgroundScheduler(timezone="Asia/Seoul")

def get_approval_key():
    global approval_key
    url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"
    with httpx.Client() as client:
        res = client.post(url, json={
            "grant_type": "client_credentials",
            "appkey": APP_KEY,
            "secretkey": APP_SECRET
        })
        if res.status_code == 200:
            approval_key = res.json()["approval_key"]
            print("✅ 새 approval_key 발급:", approval_key)
        else:
            print("❌ 발급 실패:", res.text)

def start_scheduler():
    get_approval_key()
    scheduler.add_job(get_approval_key, "cron", hour=0, minute=0)
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
