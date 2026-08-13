import requests
import streamlit as st


FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def get_fred_series(api_key, series_id, limit=1):
    """
    Retrieve the latest observation for a FRED series.
    """

    params = {
        "api_key": api_key,
        "series_id": series_id,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit
    }

    response = requests.get(
        FRED_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    observations = data.get(
        "observations",
        []
    )

    if not observations:
        return None

    return observations[0]


def get_macro_data():
    """
    Retrieve important macroeconomic indicators
    from FRED.
    """

    try:
        api_key = st.secrets["FRED_API_KEY"]

    except Exception:
        return {
            "status": "not_connected",
            "message": (
                "FRED_API_KEY is not configured "
                "in Streamlit Secrets."
            )
        }


    indicators = {
        "Federal Funds Rate": "FEDFUNDS",
        "10-Year Treasury Yield": "DGS10",
        "Consumer Price Index": "CPIAUCSL",
        "Unemployment Rate": "UNRATE"
    }


    results = {}


    for name, series_id in indicators.items():

        try:

            observation = get_fred_series(
                api_key,
                series_id
            )

            if observation:

                results[name] = {
                    "series_id": series_id,
                    "date": observation.get(
                        "date"
                    ),
                    "value": observation.get(
                        "value"
                    )
                }

            else:

                results[name] = {
                    "series_id": series_id,
                    "error": "No observation returned."
                }


        except Exception as error:

            results[name] = {
                "series_id": series_id,
                "error": str(error)
            }


    return results


def format_macro_for_ai(macro_data):
    """
    Convert macroeconomic data into clean
    research context for the AI.
    """

    if not macro_data:

        return """
MACROECONOMIC DATA

No macroeconomic data was retrieved.

Do not invent macroeconomic conditions.
"""


    if macro_data.get("status") == "not_connected":

        return f"""
MACROECONOMIC DATA

{macro_data.get("message")}

Do not invent macroeconomic conditions.
"""


    lines = [
        "MACROECONOMIC DATA",
        "",
        "Source: FRED",
        ""
    ]


    for name, data in macro_data.items():

        lines.append(
            f"{name}:"
        )


        if "error" in data:

            lines.append(
                f"Error: {data['error']}"
            )

        else:

            lines.append(
                f"Series ID: "
                f"{data.get('series_id')}"
            )

            lines.append(
                f"Date: "
                f"{data.get('date')}"
            )

            lines.append(
                f"Value: "
                f"{data.get('value')}"
            )


        lines.append("")


    lines.extend([
        "IMPORTANT:",
        "",
        "These are reported economic observations, "
        "not predictions.",
        "",
        "Do not invent missing macroeconomic data."
    ])


    return "\n".join(lines) 
