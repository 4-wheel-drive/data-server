def detect_swing_points(highs, lows, lookback=2):
    swing_highs, swing_lows = [], []
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback+1]):
            swing_highs.append(i)
        if lows[i] == min(lows[i-lookback:i+lookback+1]):
            swing_lows.append(i)
    return swing_highs, swing_lows
