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
from app.domain.daily_quotes.candles.data_processor import process_daily_data
from app.config.redis_client import redis_client  # ✅ Redis client import

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KIS_REST_API_URL = os.getenv("KIS_REST_API_URL", "https://openapivts.koreainvestment.com:29443")


def get_daily_quotes(symbol: str, symbol_name: str = None,
                     start_date: str = None, end_date: str = None):
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
        "tr_id": "FHKST01010400"
    }

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol,
        "fid_input_date_1": start_date,
        "fid_input_date_2": end_date,
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "1"
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
    """Redis에서 Access Token 조회"""
    try:
        token = redis_client.get("hanto:access_token")
        if token:
            return token.decode("utf-8") if isinstance(token, bytes) else token
        else:
            print("❌ Redis에 Access Token이 없습니다.")
            return None
    except Exception as e:
        print(f"❌ Redis Access Token 조회 실패: {e}")
        return None


def calculate_technical_indicators(quotes_data):
    """보조지표 계산"""
    if not quotes_data or len(quotes_data) < 20:
        print("보조지표 계산을 위한 충분한 데이터가 없습니다.")
        return None

    try:
        df = pd.DataFrame(quotes_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        indicators = {}
        closes = df['close'].tolist()

        # RSI
        if len(df) >= 14:
            indicators['rsi'] = compute_rsi(closes)

        # MACD
        if len(df) >= 26:
            indicators['macd'] = compute_macd(closes)

        # Bollinger Bands
        if len(df) >= 20:
            indicators['bollinger_bands'] = compute_bollinger_bands(closes)

        # SMA
        sma_dict = compute_sma(closes, windows=[5, 10, 20, 60])
        indicators.update(sma_dict)

        # EMA
        ema_dict = compute_ema(closes, windows=[5, 10, 20, 60])
        indicators.update(ema_dict)

        return indicators
    except Exception as e:
        print(f"보조지표 계산 에러: {e}")
        return None
