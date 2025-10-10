from apscheduler.schedulers.background import BackgroundScheduler
from domain.daily_quotes.daily_quotes_service import get_daily_quotes, calculate_technical_indicators, get_access_token
from datetime import datetime, timedelta
import os
import time

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

def get_watchlist_symbols():
    """
    watchlist.txt 파일에서 모니터링할 종목 리스트를 가져오는 함수
    """
    try:
        # 프로젝트 루트 디렉토리의 watchlist.txt 파일을 찾기
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        watchlist_path = os.path.join(project_root, "watchlist.txt")
        
        with open(watchlist_path, "r", encoding="utf-8") as f:
            symbols = []
            for line in f.readlines():
                line = line.strip()
                # 주석이 아니고 비어있지 않은 줄만 처리
                if line and not line.startswith("#"):
                    # 종목코드만 추출 (주석 제거)
                    symbol = line.split('#')[0].strip()
                    if symbol and len(symbol) == 6:  # 종목코드는 6자리
                        symbols.append(line)  # 원본 라인 유지 (주석 포함)
            
            if symbols:
                print(f"📋 watchlist.txt에서 {len(symbols)}개 종목 로드 완료")
                return symbols
            else:
                print("⚠️ watchlist.txt에 유효한 종목이 없습니다.")
                return []
                
    except FileNotFoundError:
        print("❌ watchlist.txt 파일을 찾을 수 없습니다.")
        print(f"   찾은 경로: {watchlist_path}")
        print("   프로젝트 루트에 watchlist.txt 파일을 생성하고 종목코드를 입력하세요.")
        return []
    except Exception as e:
        print(f"❌ watchlist.txt 파일 읽기 오류: {e}")
        return []

# 모니터링할 종목 리스트
WATCHLIST_SYMBOLS = get_watchlist_symbols()

def collect_daily_quotes():
    """
    일별 시세 데이터를 수집하고 보조지표를 계산하는 함수
    새벽 2시에 실행됨
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 일별 시세 데이터 수집 시작")
    
    # 환경 변수 확인
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    
    if not app_key or not app_secret:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        print("   다음 단계를 따라 설정하세요:")
        print("   1. 프로젝트 루트에 .env 파일을 생성하세요")
        print("   2. .env 파일에 다음 내용을 추가하세요:")
        print("      APP_KEY=your_app_key_here")
        print("      APP_SECRET=your_app_secret_here")
        print("   3. 한국투자증권 개발자센터(https://apiportal.koreainvestment.com/)에서 키를 발급받아 실제 값으로 교체하세요")
        return
    
    if not WATCHLIST_SYMBOLS:
        print("❌ 모니터링할 종목이 없습니다.")
        print("   watchlist.txt 파일에 유효한 종목코드를 추가하세요.")
        return
    
    token = get_access_token()
    if not token:
        print("❌ Access Token 발급 실패로 인해 데이터 수집을 중단합니다.")
        return
    
    print(f"📊 {len(WATCHLIST_SYMBOLS)}개 종목 데이터 수집 시작")
    
    success_count = 0
    fail_count = 0
    
    for symbol_info in WATCHLIST_SYMBOLS:
        # 주석 제거하고 종목코드와 종목명 추출
        symbol = symbol_info.split('#')[0].strip()
        symbol_name = symbol_info.split('#')[1].strip() if '#' in symbol_info else symbol
        
        if not symbol or len(symbol) != 6:
            continue
            
        try:
            # API 호출 제한을 위한 딜레이 (3초 대기)
            time.sleep(3)
            
            # 최근 30일 데이터 조회
            data = get_daily_quotes(symbol, symbol_name)
            
            if data and data.get('data'):
                success_count += 1
                print(f"✅ {symbol} ({symbol_name}): {data.get('count', 0)}일 데이터 수집 완료")
                
                # 보조지표 계산
                indicators = calculate_technical_indicators(data['data'])
                
                if indicators:
                    print(f"📊 {symbol} 보조지표:")
                    if indicators.get('rsi'):
                        print(f"   RSI: {indicators['rsi']:.2f}")
                    if indicators.get('macd'):
                        macd = indicators['macd']
                        print(f"   MACD: {macd.get('macd', 0):.2f}")
                    if indicators.get('bollinger_bands'):
                        bb = indicators['bollinger_bands']
                        print(f"   볼린저밴드: {bb.get('upper', 0):.0f} ~ {bb.get('lower', 0):.0f}")
                    
                    # 이동평균 지표 출력
                    if indicators.get('sma20'):
                        print(f"   SMA20: {indicators['sma20']:.0f}")
                    if indicators.get('sma50'):
                        print(f"   SMA50: {indicators['sma50']:.0f}")
                    if indicators.get('ema8'):
                        print(f"   EMA8: {indicators['ema8']:.0f}")
                    if indicators.get('ema21'):
                        print(f"   EMA21: {indicators['ema21']:.0f}")
                    if indicators.get('ema50'):
                        print(f"   EMA50: {indicators['ema50']:.0f}")
                
                # TODO: 여기에 데이터베이스 저장 로직 추가
                # save_to_database(symbol, data, indicators)
                
            else:
                fail_count += 1
                print(f"❌ {symbol} ({symbol_name}): 데이터 수집 실패")
                
        except Exception as e:
            fail_count += 1
            print(f"❌ {symbol} ({symbol_name}) 처리 중 에러: {e}")
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 일별 시세 데이터 수집 완료")
    print(f"📊 결과: 성공 {success_count}개, 실패 {fail_count}개")

def start_daily_quotes_scheduler():
    """
    일별 시세 수집 스케줄러 시작
    매일 새벽 2시에 실행
    """
    print("일별 시세 스케줄러 시작 - 매일 새벽 2시 실행")
    
    # 즉시 한 번 실행 (테스트용)
    collect_daily_quotes()
    
    # 매일 새벽 2시에 실행
    scheduler.add_job(
        collect_daily_quotes,
        "cron",
        hour=2,
        minute=0,
        id="daily_quotes_collection"
    )
    
    scheduler.start()

def shutdown_daily_quotes_scheduler():
    """
    일별 시세 수집 스케줄러 종료
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("일별 시세 스케줄러 종료")

# 테스트용 함수
def test_collect_daily_quotes():
    """
    테스트용 함수 - 즉시 실행
    """
    collect_daily_quotes()

if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_collect_daily_quotes()

