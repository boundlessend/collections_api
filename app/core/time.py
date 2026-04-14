from datetime import datetime
from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def moscow_now() -> datetime:
    """возвращает текущее время по москве"""

    return datetime.now(MOSCOW_TZ)


def to_moscow(value: datetime) -> datetime:
    """приводит дату и время к московскому часовому поясу"""

    if value.tzinfo is None:
        return value.replace(tzinfo=MOSCOW_TZ)
    return value.astimezone(MOSCOW_TZ)
