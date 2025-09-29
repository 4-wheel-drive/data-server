import httpx
import os
import json
import pandas as pd
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.domain.daily_quotes.indicators.rsi import compute_rsi
from app.domain.daily_quotes.indicators.macd import compute_macd
from app.domain.daily_quotes.indicators.bollinger import compute_bollinger_bands
from app.domain.daily_quotes.indicators.moving_average import compute_sma, compute_ema
from app.domain.daily_quotes.candles.data_processor import process_daily_data

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KIS_REST_API_URL = os.getenv("KIS_REST_API_URL", "https://openapivts.koreainvestment.com:29443")

class DailyQuotesService:
    def __init__(self):
        self.app_key = APP_KEY
        self.app_secret = APP_SECRET
        self.base_url = KIS_REST_API_URL
        self.access_token = None
        self.token_expires_at = None
        self.last_token_request_time = 0
    
    def get_daily_quotes(self, symbol: str, symbol_name: str = None, start_date: str = None, end_date: str = None):
        """
        일별 시세 데이터를 가져오는 함수
        
        Args:
            symbol (str): 종목코드 (예: "005930")
            start_date (str): 시작 날짜 (YYYYMMDD 형식, None이면 30일 전)
            end_date (str): 종료 날짜 (YYYYMMDD 형식, None이면 오늘)
        
        Returns:
            dict: 일별 시세 데이터
        """
        # 날짜 설정
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.get_access_token()}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010400"
        }
        
        params = {
            "fid_cond_mrkt_div_code": "J",  # 주식시장
            "fid_input_iscd": symbol,        # 종목코드
            "fid_input_date_1": start_date, # 시작일
            "fid_input_date_2": end_date,   # 종료일
            "fid_period_div_code": "D",     # 일봉
            "fid_org_adj_prc": "1"          # 수정주가 반영
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return process_daily_data(data, symbol, symbol_name)
                else:
                    print(f"❌ 일별 시세 조회 실패: {response.status_code}")
                    print(f"   응답 내용: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ 일별 시세 요청 에러: {e}")
            return None
    
    def get_access_token(self):
        """
        Access Token을 발급받는 함수 (access_token_scheduler에서 발급된 토큰 사용)
        """
        # access_token_scheduler에서 발급된 토큰을 사용
        from app.schedule.access_token_scheduler import get_access_token as scheduler_get_token
        
        # 스케줄러에서 토큰을 가져오기 (이미 발급된 토큰 사용)
        token = scheduler_get_token()
        if token:
            self.access_token = token
            return token
        
        # 토큰이 없으면 직접 발급 시도 (1분당 1회 제한 고려)
        current_time = time.time()
        
        # 토큰이 있고 아직 유효한 경우
        if self.access_token and self.token_expires_at and current_time < self.token_expires_at:
            return self.access_token
        
        # 1분 제한 확인 (마지막 요청 후 60초 경과 확인)
        if current_time - self.last_token_request_time < 60:
            wait_time = 60 - (current_time - self.last_token_request_time)
            print(f"토큰 발급 제한으로 인해 {wait_time:.1f}초 대기 중...")
            time.sleep(wait_time)
        
        # APP_KEY, APP_SECRET 확인
        if not self.app_key or not self.app_secret:
            print("❌ APP_KEY 또는 APP_SECRET이 설정되지 않았습니다.")
            print("   .env 파일에 다음을 설정하세요:")
            print("   APP_KEY=your_app_key")
            print("   APP_SECRET=your_app_secret")
            return None
            
        url = f"{self.base_url}/oauth2/tokenP"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            self.last_token_request_time = time.time()
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 86400)  # 기본 24시간
                    
                    # 토큰 만료 시간 설정 (5분 여유)
                    self.token_expires_at = current_time + expires_in - 300
                    
                    print(f"✅ Access Token 발급 성공: {self.access_token[:20]}...")
                    print(f"   만료 시간: {datetime.fromtimestamp(self.token_expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
                    return self.access_token
                else:
                    print(f"❌ Access Token 발급 실패: {response.status_code}")
                    print(f"   응답: {response.text}")
                    
                    # APP_KEY/APP_SECRET 오류인지 확인
                    if "EGW00133" in response.text:
                        print("   → 1분당 1회 제한에 걸렸습니다. 잠시 후 다시 시도하세요.")
                    elif "EGW00121" in response.text or "invalid" in response.text.lower():
                        print("   → APP_KEY 또는 APP_SECRET이 잘못되었을 수 있습니다.")
                        print("   → 한국투자증권 개발자센터에서 발급받은 키를 확인하세요.")
                    
                    return None
                    
        except Exception as e:
            print(f"❌ Access Token 요청 에러: {e}")
            return None
    
    
    def calculate_technical_indicators(self, quotes_data):
        """
        보조지표를 계산하는 함수
        
        Args:
            quotes_data (list): 일별 시세 데이터 리스트
            
        Returns:
            dict: 보조지표 데이터
        """
        if not quotes_data or len(quotes_data) < 20:
            print("보조지표 계산을 위한 충분한 데이터가 없습니다.")
            return None
        
        try:
            df = pd.DataFrame(quotes_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            indicators = {}
            
            # RSI 계산
            if len(df) >= 14:
                indicators['rsi'] = compute_rsi(df['close'].tolist())
            
            # MACD 계산
            if len(df) >= 26:
                macd_data = compute_macd(df['close'].tolist())
                indicators['macd'] = macd_data
            
            # 볼린저 밴드 계산
            if len(df) >= 20:
                bb_data = compute_bollinger_bands(df['close'].tolist())
                indicators['bollinger_bands'] = bb_data
            
            # 이동평균 계산 (구체적인 기간별)
            closes = df['close'].tolist()
            
            # SMA (Simple Moving Average)
            if len(df) >= 20:
                indicators["sma20"] = compute_sma(closes, 20).iloc[-1]
            if len(df) >= 50:
                indicators["sma50"] = compute_sma(closes, 50).iloc[-1]
            
            # EMA (Exponential Moving Average)
            if len(df) >= 8:
                indicators["ema8"] = compute_ema(closes, 8).iloc[-1]
            if len(df) >= 21:
                indicators["ema21"] = compute_ema(closes, 21).iloc[-1]
            if len(df) >= 50:
                indicators["ema50"] = compute_ema(closes, 50).iloc[-1]
            
            return indicators
            
        except Exception as e:
            print(f"보조지표 계산 에러: {e}")
            return None
    

