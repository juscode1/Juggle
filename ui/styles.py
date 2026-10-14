from datetime import date, datetime
from html import escape
from zoneinfo import ZoneInfo


PRIORITY_COLORS = {
    "High": "#ff4b4b",
    "Medium": "#f5a524",
    "Low": "#21c27a",
}


def today_manila():
    return datetime.now(ZoneInfo("Asia/Manila")).date()


def to_date(value):
    """Convert a deadline into a date object."""

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def priority_badge(priority):
    label = str(priority).title()
    color = PRIORITY_COLORS.get(label, "#8b95a1")

    return (
        f'<span style="display:inline-block;padding:2px 10px;'
        f'border-radius:999px;font-size:12px;font-weight:600;'
        f'white-space:nowrap;color:{color};background:{color}22;'
        f'border:1px solid {color}66;">'
        f'{escape(label)}</span>'
    )


def chip(label, value, color=None):
    value_color = f"color:{color};" if color else ""

    return (
        '<div style="flex:1 1 0;min-width:110px;padding:8px 16px;'
        'border-radius:10px;border:1px solid rgba(128,128,128,0.35);">'
        f'<div style="font-size:12px;opacity:0.7;">'
        f'{escape(str(label))}</div>'
        f'<div style="font-size:18px;font-weight:600;{value_color}">'
        f'{escape(str(value))}</div></div>'
    )
