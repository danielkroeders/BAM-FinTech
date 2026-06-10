def format_number(value, decimals=0):
    number = float(value)
    formatted = f"{number:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_integer(value):
    return format_number(value, decimals=0)


def format_currency(value, decimals=0):
    return f"€ {format_number(value, decimals)}"


def format_currency_input(value):
    return f"€{format_number(value, 2)}"


def parse_eu_number(value):
    text = str(value).strip().replace("€", "").replace(" ", "").replace("\u00a0", "")
    if not text:
        raise ValueError("Enter a number.")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif "." in text:
        parts = text.split(".")
        if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
            text = "".join(parts)
    return float(text)


def format_percent(value, decimals=1):
    return f"{format_number(float(value) * 100, decimals)}%"


def format_score(value, decimals=2):
    return format_number(value, decimals)


def format_months(value, decimals=0):
    return f"{format_number(value, decimals)} mo"
