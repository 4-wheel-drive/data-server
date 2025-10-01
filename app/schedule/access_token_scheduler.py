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
    한국투자증권에서 REST API용 Access Token 발급
"""
def get_access_token():
    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET
            })

        if res.status_code == 200:
            access_token = res.json().get("access_token")
            print("access token 발급:", access_token)
            redis_client.setex("hanto:access_token", 86400, access_token)
        else:
            print("Access Token 발급 실패:", res.status_code, res.text)

    except Exception as e:
        print("Access Token 요청 에러:", e)

"""
    서버 시작 시 바로 발급하고, 12시마다 갱신.
"""
def start_access_token_scheduler():
    get_access_token()
    scheduler.add_job(get_access_token, "cron", hour=0, minute=0)
    scheduler.start()

"""
    서버 종료 시 스케줄러 정리
"""
def shutdown_access_token_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

def get_access_token_from_cache() -> str | None:
    return redis_client.get("access_token")