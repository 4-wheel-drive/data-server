import httpx
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from app.domain.indicators.rsi import compute_rsi
from app.domain.indicators.macd import compute_macd
from app.domain.indicators.bollinger import compute_bollinger_bands
from app.domain.indicators.moving_average import compute_sma, compute_ema
from app.domain.indicators.vwap import compute_vwap
from app.domain.indicators.rvol import compute_rvol
from app.domain.daily_quotes.candles.data_processor import process_daily_data
from app.infra.redis_client import redis_client

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KIS_REST_API_URL = os.getenv(
    "KIS_REST_API_URL", "https://openapivts.koreainvestment.com:29443"
)


def get_daily_quotes(
    symbol: str, symbol_name: str = None, start_date: str = None, end_date: str = None
):
    """일별 시세 조회"""
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

    url = f"{KIS_REST_API_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    token = get_access_token()
    if not token:
        print("❌ Access Token 없음. 요청 중단.")
        return None

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010400",
    }

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol,
        "fid_input_date_1": start_date,
        "fid_input_date_2": end_date,
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "1",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, headers=headers, params=params)
            if res.status_code == 200:
                return process_daily_data(res.json(), symbol, symbol_name)
            else:
                print(f"❌ 일별 시세 조회 실패: {res.status_code}")
                print(f"   응답 내용: {res.text}")
                return None
    except Exception as e:
        print(f"❌ 일별 시세 요청 에러: {e}")
        return None


def get_access_token() -> str | None:
    """Redis에서 Access Token 조회 (한투 REST API용)"""
    try:
        # data-server 전용 한투 API token
        token = redis_client.get("kis:data-server:access-token")
        
        if not token:
            # 없으면 직접 발급
            print("⚠️  Redis에 Access Token이 없습니다. 직접 발급 시도...")
            token = issue_new_access_token()
        
        if token:
            return token.decode("utf-8") if isinstance(token, bytes) else token
        else:
            print("❌ Access Token 발급 실패")
            return None
    except Exception as e:
        print(f"❌ Redis Access Token 조회 실패: {e}")
        return None


def issue_new_access_token() -> str | None:
    """한투 API에서 직접 Access Token 발급"""
    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET
            })
            
            if res.status_code == 200:
                data = res.json()
                access_token = data.get("access_token")
                expires_in = data.get("expires_in", 86400)
                
                # Redis에 저장 (TTL 설정)
                redis_client.setex("kis:data-server:access-token", expires_in - 60, access_token)
                print(f"✅ 새 Access Token 발급 성공 (유효기간: {expires_in}초)")
                
                return access_token
            else:
                print(f"❌ Access Token 발급 실패: {res.status_code}")
                print(f"   응답: {res.text}")
                return None
    except Exception as e:
        print(f"❌ Access Token 발급 에러: {e}")
        return None


def get_52week_high_low(symbol: str) -> dict:
    """
    한투 API에서 52주 고가/저가 조회
    
    Args:
        symbol: 종목코드
    
    Returns:
        dict: {"week52_high": 96000, "week52_low": 49900, "week52_range": 46100}
    """
    url = f"{KIS_REST_API_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    
    token = get_access_token()
    if not token:
        return {}
    
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100",
    }
    
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol,
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, headers=headers, params=params)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("rt_cd") == "0":
                    output = data.get("output", {})
                    
                    week52_high = int(output.get("d250_hgpr", 0))
                    week52_low = int(output.get("d250_lwpr", 0))
                    
                    if week52_high > 0 and week52_low > 0:
                        return {
                            "week52_high": week52_high,
                            "week52_low": week52_low,
                            "week52_range": week52_high - week52_low
                        }
            
            return {}
    except Exception as e:
        print(f"⚠️  52주 고저 조회 에러: {e}")
        return {}


def calculate_technical_indicators(quotes_data, symbol=None):
    """
    보조지표 계산 및 Redis 저장
    
    Args:
        quotes_data: 일봉 데이터 리스트
        symbol: 종목코드 (Redis 저장용)
    
    Returns:
        dict: 계산된 지표들
    """
    if not quotes_data or len(quotes_data) < 20:
        print("보조지표 계산을 위한 충분한 데이터가 없습니다.")
        return None

    try:
        df = pd.DataFrame(quotes_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        indicators = {}
        closes = df["close"].tolist()
        highs = df["high"].tolist()
        lows = df["low"].tolist()
        volumes = df["volume"].tolist()

        # RSI (7, 14, 21)
        rsi_dict = compute_rsi(closes, periods=[7, 14, 21])
        indicators.update(rsi_dict)

        # MACD (12, 26, 9)
        macd_dict = compute_macd(closes, short=12, long=26, signal=9)
        indicators.update(macd_dict)

        # Bollinger Bands (9, 20, 50, 60, 200)
        bb_dict = compute_bollinger_bands(closes, periods=[9, 20, 50, 60, 200], num_std=2)
        indicators.update(bb_dict)

        # SMA (9, 20, 50, 60, 200)
        sma_dict = compute_sma(closes, periods=[9, 20, 50, 60, 200])
        indicators.update(sma_dict)

        # EMA (9, 20, 50, 60, 200)
        ema_dict = compute_ema(closes, periods=[9, 20, 50, 60, 200])
        indicators.update(ema_dict)
        
        # VWAP
        vwap = compute_vwap(closes, volumes)
        if vwap is not None:
            indicators['vwap'] = vwap
        
        # RVOL
        rvol = compute_rvol(volumes, period=20)
        if rvol is not None:
            indicators['rvol_20'] = rvol
        
        # 52주 고가/저가 (API에서 직접 조회)
        week52_data = get_52week_high_low(symbol)
        if week52_data:
            indicators.update(week52_data)

        # Redis 저장
        if symbol and indicators:
            indicator_key = f"I:{symbol}:1d"
            # None 값 제거
            clean_indicators = {k: str(v) for k, v in indicators.items() if v is not None}
            if clean_indicators:
                redis_client.hset(indicator_key, mapping=clean_indicators)
                print(f"✅ Redis 저장: {indicator_key} ({len(clean_indicators)}개 지표)")

        return indicators
    except Exception as e:
        print(f"보조지표 계산 에러: {e}")
        return None
