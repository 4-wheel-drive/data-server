import pandas as pd
from datetime import datetime

def process_daily_data(data, symbol_code=None, symbol_name=None):
    """
    API 응답 데이터를 처리하는 함수
    
    Args:
        data (dict): API 응답 데이터
        symbol_code (str): 종목코드
        symbol_name (str): 종목명
        
    Returns:
        dict: 처리된 일별 시세 데이터
    """
    try:
        if data.get("rt_cd") != "0":
            print(f"API 에러: {data.get('msg1', 'Unknown error')}")
            return None
        
        output = data.get("output", [])
        processed_data = []
        
        for item in output:
            processed_item = {
                "date": item.get("stck_bsop_date"),      # 날짜
                "open": int(item.get("stck_oprc", 0)),   # 시가
                "high": int(item.get("stck_hgpr", 0)),   # 고가
                "low": int(item.get("stck_lwpr", 0)),    # 저가
                "close": int(item.get("stck_clpr", 0)),  # 종가
                "volume": int(item.get("acml_vol", 0)),  # 거래량
                "change": int(item.get("prdy_vrss", 0)),  # 전일대비
                "change_rate": float(item.get("prdy_ctrt", 0))  # 전일대비율 (prdy_ctrt 사용)
            }
            processed_data.append(processed_item)
        
        # 종목명 결정 (watchlist.txt에서 전달받은 종목명 사용)
        final_symbol_name = symbol_name if symbol_name else f"종목{symbol_code}" if symbol_code else "알 수 없는 종목"
        
        return {
            "symbol": final_symbol_name,
            "data": processed_data,
            "count": len(processed_data)
        }
        
    except Exception as e:
        print(f"데이터 처리 에러: {e}")
        return None

