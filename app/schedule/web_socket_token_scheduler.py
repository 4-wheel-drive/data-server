from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

"""
    한국투자증권 OpenAPI에서 REST API용 Access Token 발급
"""
def get_approval_key():
    url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"
    
    try:
        with httpx.Client() as client:
            res = client.post(url, json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "secretkey": APP_SECRET
            })

            if res.status_code == 200:
                approval_key = res.json()["approval_key"]
                print("새 approval_key 발급:", approval_key)
            else:
                print("발급 실패:", res.text)
    except Exception as e:
        print("Access Token 요청 에러:", e)

"""
    서버 시작 시 바로 발급하고, 12시마다 갱신.
"""
def start_scheduler():
    get_approval_key()
    scheduler.add_job(get_approval_key, "cron", hour=0, minute=0)
    scheduler.start()

"""
    서버 종료 시 스케줄러 정리
"""
def shutdown_scheduler():
    scheduler.shutdown()
