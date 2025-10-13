# def compute_cumulative_values(candles):
#     """누적 거래량 / 거래대금"""
#     volumes = [c["volume"] for c in candles]
#     cumulative_volume = sum(volumes)
#     cumulative_value = sum([c["close"] * c["volume"] for c in candles])
#     return {
#         "cumulative_volume": cumulative_volume,
#         "cumulative_value": cumulative_value,
#     }
