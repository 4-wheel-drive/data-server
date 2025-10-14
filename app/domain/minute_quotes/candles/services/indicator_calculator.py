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


def calculate_and_save_indicators(symbol: str, timeframe: str):
    """
    특정 종목/타임프레임의 캔들 데이터를 읽어서 지표 계산 후 Redis 저장 & Kafka 발행
    
    Args:
        symbol: 종목코드 (예: "005930")
        timeframe: 타임프레임 (예: "1m", "5m", "15m", "1h", "4h")
    
    Returns:
        dict: 계산된 지표들
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
    opens = [float(c['o']) for c in candles]
    
    if not prices:
        return {}
    
    # 3. 지표 계산
    indicators = {}
    
    # RSI (7, 14, 21)
    try:
        rsi_dict = compute_rsi(prices, periods=[7, 14, 21])
        indicators.update(rsi_dict)
    except Exception as e:
        print(f"⚠️  RSI 계산 에러: {e}")
    
    # MACD (12, 26, 9)
    try:
        macd_dict = compute_macd(prices, short=12, long=26, signal=9)
        indicators.update(macd_dict)
    except Exception as e:
        print(f"⚠️  MACD 계산 에러: {e}")
    
    # Bollinger Bands (9, 20, 50, 60, 200)
    try:
        bb_dict = compute_bollinger_bands(prices, periods=[9, 20, 50, 60, 200], num_std=2)
        indicators.update(bb_dict)
    except Exception as e:
        print(f"⚠️  Bollinger Bands 계산 에러: {e}")
    
    # SMA (9, 20, 50, 60, 200)
    try:
        sma_dict = compute_sma(prices, periods=[9, 20, 50, 60, 200])
        indicators.update(sma_dict)
    except Exception as e:
        print(f"⚠️  SMA 계산 에러: {e}")
    
    # EMA (9, 20, 50, 60, 200)
    try:
        ema_dict = compute_ema(prices, periods=[9, 20, 50, 60, 200])
        indicators.update(ema_dict)
    except Exception as e:
        print(f"⚠️  EMA 계산 에러: {e}")
    
    # VWAP
    try:
        vwap = compute_vwap(prices, volumes)
        if vwap is not None:
            indicators['vwap'] = vwap
    except Exception as e:
        print(f"⚠️  VWAP 계산 에러: {e}")
    
    # RVOL
    try:
        rvol = compute_rvol(volumes, period=20)
        if rvol is not None:
            indicators['rvol_20'] = rvol
    except Exception as e:
        print(f"⚠️  RVOL 계산 에러: {e}")
    
    # Opening Range (15분봉만)
    if timeframe == '15m':
        try:
            or_dict = compute_opening_range_indicators(highs, lows, prices)
            indicators.update(or_dict)
        except Exception as e:
            print(f"⚠️  Opening Range 계산 에러: {e}")
    
    if not indicators:
        print(f"⚠️  [{symbol}:{timeframe}] 계산된 지표 없음")
        return {}
    
    # None 값 제거
    clean_indicators = {k: v for k, v in indicators.items() if v is not None}
    
    # 4. Kafka 발행 (분봉 지표는 Kafka에만!)
    try:
        topic = f"indicators.{symbol}.{timeframe}"
        message = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": candles[-1]['t'] if candles else None,
            "indicators": clean_indicators
        }
        producer.produce(
            topic,
            value=json.dumps(message, ensure_ascii=False),
            callback=delivery_report
        )
        producer.poll(0)
        print(f"📤 [{symbol}:{timeframe}] Kafka 발행: {len(clean_indicators)}개 지표")
    except Exception as e:
        print(f"❌ Kafka 발행 에러: {e}")
    
    return indicators

