import streamlit as st
from collections import Counter
from datetime import date, timedelta
from supabase_client import get_supabase


# Date range shown in the heatmap
START = date(2026, 9, 28)
END = date(2026, 12, 20)

# Sizes
CELL = 32
GAP = 6
HEIGHT = 348

# Colors (teal + gold theme)
LABEL_COLOR = "#7A705F"
HOVER_COLOR = "#2B2620"
LEVEL_0 = "#E4D9C2"   # no tasks
LEVEL_1 = "#F0D58A"   # 1 task
LEVEL_2 = "#D9A93B"   # 2-3 tasks
LEVEL_3 = "#9A6B12"   # 4+ tasks


def load_activity():
    """Return a count of completed tasks per day for the current user."""
    user_id = st.session_state.get("user_id")

    if not user_id:
        return Counter()

    response = (
        get_supabase()
        .table("tasks")
        .select("completed_date")
        .eq("user_id", user_id)
        .eq("completed", True)
        .not_.is_("completed_date", "null")
        .execute()
    )

    return Counter(
        str(row["completed_date"])[:10]
        for row in response.data
    )


def get_level(count):
    """Convert a task count into a color level from 0 to 3."""
    if count == 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    return 3


def build_weeks(activity):
    """Build the HTML for every week column."""
    weeks_html = ""
    current = START
    prev_month = None

    while current <= END:

        month_label = ""

        if current.month != prev_month:
            month_label = current.strftime("%b")
            prev_month = current.month

        weeks_html += '<div class="week">'
        weeks_html += f'<div class="month">{month_label}</div>'

        for i in range(7):

            day = current + timedelta(days=i)

            if day > END:
                weeks_html += '<div class="cell empty"></div>'
                continue

            count = activity[day.isoformat()]
            level = get_level(count)
            plural = "" if count == 1 else "s"

            tip = (
                f"{count} completed task{plural} "
                f"on {day.strftime('%B %d, %Y')}"
            )

            weeks_html += (
                f'<div class="cell level-{level}" title="{tip}"></div>'
            )

        weeks_html += "</div>"
        current += timedelta(weeks=1)

    return weeks_html


def show_activity_heatmap():

    try:
        activity = load_activity()
    except Exception:
        st.error("Unable to load activity history. Please try again.")
        return

    weeks_html = build_weeks(activity)

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days_html = "".join(f"<div>{name}</div>" for name in day_names)

    html = f"""
    <style>
        body {{
            margin: 0;
            font-family: "DM Sans", "Source Sans Pro", sans-serif;
            font-size: 12px;
            color: {LABEL_COLOR};
        }}

        .wrap {{
            display: flex;
            justify-content: center;
            padding: 12px 0;
        }}

        .inner {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .heatmap {{
            display: flex;
            gap: 8px;
        }}

        .days {{
            display: flex;
            flex-direction: column;
            gap: {GAP}px;
            padding-top: {22 + GAP}px;
        }}

        .days div {{
            width: 40px;
            height: {CELL}px;
            line-height: {CELL}px;
        }}

        .weeks {{
            display: flex;
            gap: {GAP}px;
        }}

        .week {{
            display: flex;
            flex-direction: column;
            gap: {GAP}px;
        }}

        .month {{
            height: 22px;
            line-height: 22px;
            white-space: nowrap;
        }}

        .cell {{
            width: {CELL}px;
            height: {CELL}px;
            border-radius: 5px;
            box-sizing: border-box;
        }}

        .cell:not(.empty):hover {{
            outline: 2px solid {HOVER_COLOR};
            outline-offset: -1px;
        }}

        .level-0 {{ background: {LEVEL_0}; }}
        .level-1 {{ background: {LEVEL_1}; }}
        .level-2 {{ background: {LEVEL_2}; }}
        .level-3 {{ background: {LEVEL_3}; }}

        .legend {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 6px;
            height: 16px;
        }}

        .legend .cell {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }}
    </style>

    <div class="wrap">
        <div class="inner">

            <div class="heatmap">
                <div class="days">{days_html}</div>
                <div class="weeks">{weeks_html}</div>
            </div>

            <div class="legend">
                Less
                <div class="cell level-0"></div>
                <div class="cell level-1"></div>
                <div class="cell level-2"></div>
                <div class="cell level-3"></div>
                More
            </div>

        </div>
    </div>
    """

    st.components.v1.html(html, height=HEIGHT, scrolling=False)