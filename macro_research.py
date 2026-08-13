import requests


def get_macro_data():
    """
    Retrieve basic macroeconomic information
    from the FRED public API.

    Returns an empty result if no API key
    is configured.
    """

    return {
        "status": "not_connected",
        "message": (
            "Macro data source has not yet "
            "been connected."
        )
    }


def format_macro_for_ai(macro_data):
    """
    Convert macro data into clean evidence
    for the AI research engine.
    """

    if not macro_data:
        return """
MACROECONOMIC DATA

No macroeconomic data is currently available.

Do not invent macroeconomic conditions.
"""

    if macro_data.get("status") == "not_connected":
        return f"""
MACROECONOMIC DATA

{macro_data.get("message")}

Do not invent macroeconomic conditions.
"""

    return f"""
MACROECONOMIC DATA

{macro_data}
"""
