import json
from app.infra.redis_client import redis_client
from app.infra.kafka_producer import producer, delivery_report
from app.domain.indicators.bollinger import compute_bollinger_bands
from app.domain.indicators.rsi import compute_rsi
from app.domain.indicators.macd import compute_macd
from app.domain.indicators.moving_average import compute_sma, compute_ema
from app.domain.indicators.vwap import compute_vwap
from app.domain.indicators.rvol import compute_rvol
from app.domain.indicators.opening_range import compute_opening_range_indicators


def _safe_update(indicators: dict, compute_func, indicator_name: str):
    """안전하게 지표 계산 후 indicators에 업데이트"""
    try:
        result = compute_func()
        if result:
            indicators.update(result)
    except Exception as e:
        print(f"⚠️  {indicator_name} 계산 에러: {e}")


def _safe_compute(compute_func, indicator_name: str):
    """안전하게 단일 지표 계산"""
    try:
        return compute_func()
    except Exception as e:
        print(f"⚠️  {indicator_name} 계산 에러: {e}")
        return None


def calculate_and_save_indicators(symbol: str, timeframe: str) -> dict:
    """
    특정 종목/타임프레임의 지표 계산 및 Kafka 발행
    
    Args:
        symbol: 종목코드 (예: "005930")
        timeframe: 타임프레임 (예: "1m", "5m", "15m", "1h", "4h")
    
    Returns:
        dict: 계산된 지표 딕셔너리
    """
    # 1. Redis에서 캔들 데이터 읽기
    candle_key = f"C:{symbol}:{timeframe}"
    candles_raw = redis_client.lrange(candle_key, 0, -1)
    
    if not candles_raw:
        print(f"⚠️  [{symbol}:{timeframe}] 캔들 데이터 없음")
        return {}
    
    # 2. 캔들 파싱
    candles = [json.loads(c) for c in candles_raw]
    prices = [float(c['c']) for c in candles]
    highs = [float(c['h']) for c in candles]
    lows = [float(c['l']) for c in candles]
    volumes = [float(c['v']) for c in candles]
    
    if not prices:
        return {}
    
    # 3. 지표 계산
    indicators = {}
    
    # RSI
    _safe_update(indicators, lambda: compute_rsi(prices, periods=[7, 14, 21]), "RSI")
    
    # MACD
    _safe_update(indicators, lambda: compute_macd(prices, short=12, long=26, signal=9), "MACD")
    
    # Bollinger Bands
    _safe_update(indicators, lambda: compute_bollinger_bands(prices, periods=[20], num_std=2), "Bollinger Bands")
    
    # SMA
    _safe_update(indicators, lambda: compute_sma(prices, periods=[9, 20, 50, 60, 200]), "SMA")
    
    # EMA
    _safe_update(indicators, lambda: compute_ema(prices, periods=[9, 20, 50, 60, 200]), "EMA")
    
    # VWAP
    vwap = _safe_compute(lambda: compute_vwap(prices, volumes), "VWAP")
    if vwap is not None:
        indicators['vwap'] = vwap
    
    # RVOL
    rvol = _safe_compute(lambda: compute_rvol(volumes, period=20), "RVOL")
    if rvol is not None:
        indicators['rvol_20'] = rvol
    
    # Opening Range (15분봉만)
    if timeframe == '15m':
        _safe_update(indicators, lambda: compute_opening_range_indicators(highs, lows, prices), "Opening Range")
    
    if not indicators:
        print(f"⚠️  [{symbol}:{timeframe}] 계산된 지표 없음")
        return {}
    
    # 4. Kafka 발행 (봉 데이터 + 지표)
    _publish_to_kafka(symbol, timeframe, candles, indicators)
    
    return indicators


def _publish_to_kafka(symbol: str, timeframe: str, candles: list, indicators: dict):
    """Kafka에 지표 메시지 발행"""
    # None 값 제거
    clean_indicators = {k: v for k, v in indicators.items() if v is not None}
    
    if not clean_indicators:
        return
    
    try:
        topic = f"indicators.{symbol}.{timeframe}"
        latest_candle = candles[-1] if candles else {}
        
        message = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": latest_candle.get('t'),
            "candle": latest_candle,
            "indicators": clean_indicators
        }
        
        producer.produce(
            topic,
            value=json.dumps(message, ensure_ascii=False),
            callback=delivery_report
        )
        producer.poll(0)
        print(f"📤 [{symbol}:{timeframe}] Kafka 발행: 봉 + {len(clean_indicators)}개 지표")
    except Exception as e:
        print(f"❌ Kafka 발행 에러: {e}")

