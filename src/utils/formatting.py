# Formatting helpers for currency, ratios, scores, and compact table values.
# The app presents Dutch/EU-friendly numbers: dot thousands, comma decimals, and
# explicit EUR prefixes. These helpers keep that formatting consistent across
# pages and downloadable summaries.
def format_number(value, decimals=0):
    number = float(value)
    formatted = f"{number:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_integer(value):
    return format_number(value, decimals=0)


def format_currency(value, decimals=0):
    # Currency is display-only. Calculations should always use raw numeric
    # values before this helper is applied.
    return f"€ {format_number(value, decimals)}"


def format_currency_input(value):
    return f"€{format_number(value, 2)}"


def parse_eu_number(value):
    # Accept values copied from EU-formatted spreadsheets or typed by users,
    # normalizing them to a float for calculations.
    text = (
        str(value)
        .strip()
        .replace("€", "")
        .replace("â‚¬", "")
        .replace("EUR", "")
        .replace("eur", "")
        .replace(" ", "")
        .replace(" ", "")
    )
    if not text:
        raise ValueError("Enter a number.")
    if "," in text:
        # Dutch/EU style values use comma decimals and dot thousands, e.g. 1.234,56.
        text = text.replace(".", "").replace(",", ".")
    elif "." in text:
        parts = text.split(".")
        if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
            # A dot-only number with 3-digit groups is treated as thousands separators.
            text = "".join(parts)
    return float(text)


def format_percent(value, decimals=1):
    # Model probabilities and ratios are stored as 0-1 values and displayed as
    # percentages for analysts and SMEs.
    return f"{format_number(float(value) * 100, decimals)}%"


def format_score(value, decimals=2):
    return format_number(value, decimals)


def format_months(value, decimals=0):
    # Keep month displays compact in metric cards and dataframes.
    return f"{format_number(value, decimals)} mo"
