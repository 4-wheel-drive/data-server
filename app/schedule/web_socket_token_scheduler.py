from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import os
from dotenv import load_dotenv
from app.config.redis_client import redis_client

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

"""
    한국투자증권 OpenAPI에서 Approval Key 발급
"""
def get_approval_key():
    url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "secretkey": APP_SECRET
            })

            if res.status_code == 200:
                approval_key = res.json().get("approval_key")
                print("새 approval_key 발급:", approval_key)
                redis_client.setex("hanto:approval_key", 86400, approval_key)
            else:
                print("Approval Key 발급 실패:", res.status_code, res.text)
    except Exception as e:
        print("Approval Key 요청 에러:", e)

"""
    서버 시작 시 바로 발급하고, 매일 0시에 갱신
"""
def start_scheduler():
    get_approval_key()
    scheduler.add_job(get_approval_key, "cron", hour=0, minute=0)
    scheduler.start()

"""
    서버 종료 시 스케줄러 정리
"""
def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

"""
    Redis에서 Approval Key 꺼내기
"""
def get_approval_key_from_cache() -> str | None:
    return redis_client.get("approval_key")
