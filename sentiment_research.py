def calculate_news_sentiment(news_items):
    """
    Calculate an aggregate sentiment signal from
    processed financial news.

    Returns bullish, neutral, and bearish scores.
    """

    if not news_items:
        return {
            "status": "no_data",
            "bullish": 0,
            "neutral": 0,
            "bearish": 0,
            "article_count": 0
        }

    bullish = 0.0
    neutral = 0.0
    bearish = 0.0

    article_count = 0

    for article in news_items:

        sentiment = str(
            article.get("sentiment", "")
        ).lower()

        score = article.get(
            "sentiment_score",
            0
        )

        relevance = article.get(
            "relevance_score",
            1
        )

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        try:
            relevance = float(relevance)
        except (TypeError, ValueError):
            relevance = 1.0

        # Keep the weighting controlled.
        weight = max(
            0.0,
            min(relevance, 10.0)
        )

        if weight == 0:
            weight = 1.0

        article_count += 1

        if "bull" in sentiment or score > 0:
            bullish += abs(score) * weight

        elif "bear" in sentiment or score < 0:
            bearish += abs(score) * weight

        else:
            neutral += weight


    total = (
        bullish +
        neutral +
        bearish
    )

    if total <= 0:

        return {
            "status": "neutral",
            "bullish": 0,
            "neutral": 1,
            "bearish": 0,
            "article_count": article_count
        }


    return {
        "status": "available",

        "bullish": round(
            bullish / total * 100,
            1
        ),

        "neutral": round(
            neutral / total * 100,
            1
        ),

        "bearish": round(
            bearish / total * 100,
            1
        ),

        "article_count": article_count
    }


def format_sentiment_for_ai(sentiment_data):
    """
    Convert the sentiment calculation into
    structured research context for the AI.
    """

    if not sentiment_data:

        return """
MARKET SENTIMENT

No sentiment data is available.

Do not infer sentiment without evidence.
"""


    if sentiment_data.get("status") == "no_data":

        return """
MARKET SENTIMENT

No relevant financial-news sentiment
was available.

Do not invent market sentiment.
"""


    bullish = sentiment_data.get(
        "bullish",
        0
    )

    neutral = sentiment_data.get(
        "neutral",
        0
    )

    bearish = sentiment_data.get(
        "bearish",
        0
    )

    article_count = sentiment_data.get(
        "article_count",
        0
    )


    return f"""
MARKET SENTIMENT

Based on {article_count} processed
financial-news item(s):

Bullish sentiment: {bullish}%

Neutral sentiment: {neutral}%

Bearish sentiment: {bearish}%


IMPORTANT:

This is a news-based sentiment measure.

It is NOT a prediction.

It should be treated as supporting evidence,
not as a standalone trading signal.

Do not assume that positive sentiment
guarantees price appreciation.

Do not assume that negative sentiment
guarantees price decline.
"""
