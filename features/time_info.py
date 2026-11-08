"""Date and time answers. 'now' can be passed in so tests are predictable."""
from datetime import datetime


def time_text(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return "It is " + now.strftime("%I:%M %p").lstrip("0")


def date_text(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return f"Today is {now:%A}, {now:%B} {now.day}, {now.year}"


def day_text(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return f"Today is {now:%A}"