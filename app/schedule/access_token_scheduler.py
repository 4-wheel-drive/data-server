from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

# 토큰 파일 경로
TOKEN_FILE = "access_token.json"

# 전역 변수로 토큰 저장
current_access_token = None
token_expires_at = None

def load_token_from_file():
    """
    파일에서 토큰 정보를 로드하는 함수
    """
    global current_access_token, token_expires_at
    
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                
            current_access_token = token_data.get('access_token')
            token_expires_at = token_data.get('expires_at')
            
            # 토큰이 유효한지 확인
            current_time = time.time()
            if current_access_token and token_expires_at and current_time < token_expires_at:
                # 토큰이 유효하면 조용히 반환 (로그 출력 안함)
                return True
            else:
                print("⚠️ 저장된 토큰이 만료되었습니다.")
                return False
        else:
            print("📝 토큰 파일이 없습니다. 새로 발급받습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 토큰 파일 로드 에러: {e}")
        return False

def save_token_to_file(access_token, expires_in):
    """
    토큰 정보를 파일에 저장하는 함수
    """
    try:
        current_time = time.time()
        expires_at = current_time + expires_in - 300  # 5분 여유
        
        token_data = {
            'access_token': access_token,
            'expires_at': expires_at,
            'issued_at': current_time,
            'expires_in': expires_in
        }
        
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2)
            
        print(f"💾 토큰이 파일에 저장되었습니다.")
        print(f"   만료 시간: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 토큰 파일 저장 에러: {e}")

"""
    한국투자증권에서 REST API용 Access Token 발급
"""
def get_access_token():
    global current_access_token, token_expires_at
    
    # 먼저 파일에서 토큰을 로드해보기
    if load_token_from_file():
        return current_access_token
    
    # 토큰이 없거나 만료된 경우 새로 발급
    print("🔑 새로운 Access Token 발급 중...")
    
    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET
            })

        if res.status_code == 200:
            token_data = res.json()
            current_access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 86400)  # 기본 24시간
            
            # 토큰 만료 시간 설정 (5분 여유)
            token_expires_at = time.time() + expires_in - 300
            
            # 토큰을 파일에 저장
            save_token_to_file(current_access_token, expires_in)
            
            print(f"✅ Access Token 발급 완료 (유효기간: {expires_in/3600:.1f}시간)")
            return current_access_token
        else:
            print("❌ Access Token 발급 실패:", res.status_code, res.text)
            return None

    except Exception as e:
        print("❌ Access Token 요청 에러:", e)
        return None


"""
    서버 시작 시 토큰 로드하고, 12시마다 갱신.
"""
def start_access_token_scheduler():
    # 서버 시작 시 토큰 로드 시도
    print("🚀 Access Token 스케줄러 시작")
    
    # 토큰 발급 (파일에서 로드하거나 새로 발급)
    get_access_token()
    
    # 매일 자정에 토큰 갱신
    scheduler.add_job(get_access_token, "cron", hour=0, minute=0)
    scheduler.start()

"""
    서버 종료 시 스케줄러 정리
"""
def shutdown_access_token_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        