import asyncio
from sqlalchemy import text
from app.domain.minute_quotes.subscribe import start_multi_subscribe
from app.infra.redis_client import redis_client
from app.infra.mariadb_connection import async_session

running_task = None  # 단일 task만 존재 (하나의 WebSocket 세션)


# ─────────────────────────────────────────────
# 종목코드 가져오기
# ─────────────────────────────────────────────
# async def get_symbols(limit=20):
#     async with async_session() as session:
#         result = await session.execute(
#             text("SELECT code FROM stock LIMIT :limit"), {"limit": limit}
#         )
#         rows = result.fetchall()
#         return [str(row[0]).zfill(6) for row in rows]


# ─────────────────────────────────────────────
# 구독 시작
# ─────────────────────────────────────────────
async def start_quotes():
    """단일 WebSocket으로 여러 종목 구독"""
    global running_task
    symbols = await get_symbols(20)
    print(f"총 {len(symbols)}개 종목 실시간 구독 시작: {symbols}", flush=True)

    running_task = asyncio.create_task(start_multi_subscribe(symbols))

    try:
        await running_task
    except asyncio.CancelledError:
        print("🛑 구독 루프 중단됨", flush=True)


STOCKS = [
    {
        "code": "005930",
        "name": "삼성전자",
        "image_uri": "https://logo.example.com/samsung.png",
    },
    {
        "code": "000660",
        "name": "SK하이닉스",
        "image_uri": "https://logo.example.com/skhynix.png",
    },
    {
        "code": "035420",
        "name": "NAVER",
        "image_uri": "https://logo.example.com/naver.png",
    },
    {
        "code": "005380",
        "name": "현대자동차",
        "image_uri": "https://logo.example.com/hyundai.png",
    },
    {
        "code": "051910",
        "name": "LG화학",
        "image_uri": "https://logo.example.com/lgchem.png",
    },
    {
        "code": "006400",
        "name": "삼성SDI",
        "image_uri": "https://logo.example.com/samsungsdi.png",
    },
    {
        "code": "035720",
        "name": "카카오",
        "image_uri": "https://logo.example.com/kakao.png",
    },
    {"code": "000270", "name": "기아", "image_uri": "https://logo.example.com/kia.png"},
    {
        "code": "068270",
        "name": "셀트리온",
        "image_uri": "https://logo.example.com/celltrion.png",
    },
    {
        "code": "207940",
        "name": "삼성바이오로직스",
        "image_uri": "https://logo.example.com/samsungbio.png",
    },
    {
        "code": "005490",
        "name": "POSCO홀딩스",
        "image_uri": "https://logo.example.com/poscoholdings.png",
    },
    {
        "code": "066570",
        "name": "LG전자",
        "image_uri": "https://logo.example.com/lgelectronics.png",
    },
    {
        "code": "012330",
        "name": "현대모비스",
        "image_uri": "https://logo.example.com/hyundaimobis.png",
    },
    {
        "code": "000810",
        "name": "삼성화재",
        "image_uri": "https://logo.example.com/samsungfire.png",
    },
    {
        "code": "015760",
        "name": "한국전력",
        "image_uri": "https://logo.example.com/kepco.png",
    },
    {
        "code": "259960",
        "name": "크래프톤",
        "image_uri": "https://logo.example.com/krafton.png",
    },
    {
        "code": "086520",
        "name": "에코프로",
        "image_uri": "https://logo.example.com/ecopro.png",
    },
    {
        "code": "247540",
        "name": "에코프로비엠",
        "image_uri": "https://logo.example.com/ecoproBM.png",
    },
    {"code": "034730", "name": "SK", "image_uri": "https://logo.example.com/sk.png"},
    {
        "code": "018260",
        "name": "삼성SDS",
        "image_uri": "https://logo.example.com/samsungsds.png",
    },
]


async def get_symbols(limit=20):
    """DB 대신 하드코딩된 종목 목록 리턴"""
    return [s["code"] for s in STOCKS[:limit]]


# ─────────────────────────────────────────────
# 구독 종료
# ─────────────────────────────────────────────
async def stop_quotes():
    global running_task
    if running_task:
        print("｢WebSocket 종료 요청 수신｣", flush=True)
        running_task.cancel()
        try:
            await running_task
        except asyncio.CancelledError:
            pass
        running_task = None
        print("｢WebSocket 정상 종료｣", flush=True)
