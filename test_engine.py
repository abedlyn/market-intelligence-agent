from evidence_engine import build_evidence_summary


result = build_evidence_summary(
    technical_bullish=5,
    technical_bearish=4,

    momentum_bullish=5,
    momentum_bearish=4,

    sentiment_bullish=4,
    sentiment_bearish=4,

    fundamental_bullish=0,
    fundamental_bearish=0,

    macro_bullish=0,
    macro_bearish=0
)


print("BULLISH:", result["probabilities"]["bullish"])
print("NEUTRAL:", result["probabilities"]["neutral"])
print("BEARISH:", result["probabilities"]["bearish"])

print()
print("TOTAL:",
      result["probabilities"]["bullish"]
      + result["probabilities"]["neutral"]
      + result["probabilities"]["bearish"])
