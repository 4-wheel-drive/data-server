# import pandas as pd

# def compute_atr(highs, lows, closes, period=14):
#     df = pd.DataFrame({"high": highs, "low": lows, "close": closes})
#     df["prev_close"] = df["close"].shift(1)
#     df["tr"] = df[["high", "low", "prev_close"]].apply(
#         lambda x: max(
#             x["high"] - x["low"],
#             abs(x["high"] - x["prev_close"]),
#             abs(x["low"] - x["prev_close"])
#         ), axis=1
#     )
#     return df["tr"].rolling(period).mean()
