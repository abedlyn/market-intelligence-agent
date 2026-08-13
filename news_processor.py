from datetime import datetime


def process_news_data(news_data):
    """
    Convert raw Alpha Vantage news data into
    clean, structured market evidence.
    """

    if not isinstance(news_data, dict):
        return []

    feed = news_data.get("feed", [])

    processed = []

    for article in feed:

        title = article.get(
            "title",
            "Unknown headline"
        )

        source = article.get(
            "source",
            "Unknown source"
        )

        published = article.get(
            "time_published",
            "Unknown time"
        )

        summary = article.get(
            "summary",
            "No summary available"
        )

        sentiment = article.get(
            "overall_sentiment_label",
            "Unknown"
        )

        sentiment_score = article.get(
            "overall_sentiment_score",
            0
        )

        relevance = article.get(
            "relevance_score",
            0
        )

        url = article.get(
            "url",
            ""
        )

        processed.append({
            "title": title,
            "source": source,
            "published": published,
            "summary": summary,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "relevance_score": relevance,
            "url": url
        })

    return processed


def format_news_for_ai(processed_news):
    """
    Convert processed news into a clean research
    context for the AI.
    """

    if not processed_news:
        return "No relevant live news was found."

    sections = []

    for index, article in enumerate(
        processed_news,
        start=1
    ):

        section = f"""
NEWS ITEM {index}

Headline:
{article["title"]}

Source:
{article["source"]}

Published:
{article["published"]}

Summary:
{article["summary"]}

Source Sentiment:
{article["sentiment"]}

Sentiment Score:
{article["sentiment_score"]}

Relevance Score:
{article["relevance_score"]}

URL:
{article["url"]}
"""

        sections.append(section)

    return "\n".join(sections)
