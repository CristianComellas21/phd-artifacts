from datetime import datetime, timedelta


def matches_text(
    value: str | None,
    query: str | None,
) -> bool:
    """Return whether a value matches a case-insensitive substring query."""

    if query is None:
        return True

    if value is None:
        return False

    return query.lower() in value.lower()


def is_since(
    value: datetime | None,
    duration: timedelta | None,
) -> bool:
    """Return whether a datetime is within the given duration."""

    if duration is None:
        return True

    if value is None:
        return False

    now = datetime.now(value.tzinfo)

    return value >= now - duration


def parse_duration(value: str) -> timedelta:
    """Parse durations such as 30m, 24h, 7d or 2w."""

    import re

    match = re.fullmatch(
        r"(\d+)([mhdw])",
        value.strip().lower(),
    )

    if not match:
        raise ValueError("Invalid duration. Use formats such as 30m, 24h, 7d or 2w.")

    amount = int(match.group(1))
    unit = match.group(2)

    match unit:
        case "m":
            return timedelta(minutes=amount)
        case "h":
            return timedelta(hours=amount)
        case "d":
            return timedelta(days=amount)
        case "w":
            return timedelta(weeks=amount)

    raise ValueError(f"Unsupported duration unit: {unit}")
