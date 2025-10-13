from datetime import datetime


def parse_tick_time(hhmmss: str) -> datetime:
    """KST tick_time(HHMMSS) → datetime 객체"""
    now = datetime.now()
    hour, minute, second = int(hhmmss[:2]), int(hhmmss[2:4]), int(hhmmss[4:6])
    return now.replace(hour=hour, minute=minute, second=second, microsecond=0)
