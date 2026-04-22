import requests
import datetime
import os
import time

# 1. CONFIGURATION
# ---------------------------------------------------------
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
INTERVAL_HOURS = 48
WARNING_MINUTES = 3

# EVENT 1 (18:30 UTC)
START_DATE_1 = datetime.datetime(2026, 4, 22, 18, 30, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_1 = "1464765731336880222"

# EVENT 2 (05:00 UTC)
START_DATE_2 = datetime.datetime(2026, 4, 22, 5, 0, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_2 = "1464766114981478430"

# EVENT 3 (23:00 UTC)
START_DATE_3 = datetime.datetime(2026, 4, 22, 23, 0, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_3 = "1482438218900312207"


def get_next_event_time(start_date, interval_hours):
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - start_date
    hours_diff = diff.total_seconds() / 3600
    intervals_passed = int(hours_diff // interval_hours)
    next_interval_count = intervals_passed + 1
    next_event = start_date + datetime.timedelta(hours=next_interval_count * interval_hours)
    return next_event

def send_daily_schedule():
    next_event_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)
    next_event_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)
    next_event_3 = get_next_event_time(START_DATE_3, INTERVAL_HOURS)
    ts_1 = int(next_event_1.timestamp())
    ts_2 = int(next_event_2.timestamp())
    ts_3 = int(next_event_3.timestamp())

    payload = {
        "content": "📢 **Daily Schedule Update**",
        "embeds": [{
            "title": "Upcoming Bear Traps in the next 48-Hours",
            "description": "Here is the schedule for the upcoming Bear Traps:",
            "color": 5814783,
            "fields": [
                {"name": "Bear Trap 1", "value": f"<t:{ts_1}:F>\n(<t:{ts_1}:R>)", "inline": False},
                {"name": "Bear Trap 2", "value": f"<t:{ts_2}:F>\n(<t:{ts_2}:R>)", "inline": False},
                {"name": "Bear Trap 3", "value": f"<t:{ts_3}:F>\n(<t:{ts_3}:R>)", "inline": False}
            ]
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
    print("Daily schedule sent.")


def send_alert(event_name, event_time, role_id):
    ts = int(event_time.timestamp())

    if event_name == "Bear Trap 3":
        payload = {
            "content": f"🚨 **HEADS UP <@&{role_id}>!**",
            "embeds": [{
                "title": f"🔥 {event_name} is Starting in {WARNING_MINUTES} minutes!",
                "description": f"Join CNA if you haven't already. It begins <t:{ts}:R> at <t:{ts}:t>!",
                "color": 15548997,  # red
            }]
        }
    else:
        payload = {
            "content": f"🚨 **HEADS UP <@&{role_id}>!**",
            "embeds": [{
                "title": f"⚔️ {event_name} is Starting in {WARNING_MINUTES} minutes!",
                "description": f"Prepare yourselves! The bear trap begins <t:{ts}:R> at <t:{ts}:t>!",
                "color": 15548997,  # red
            }]
        }

    requests.post(WEBHOOK_URL, json=payload)
    print(f"Alert sent for {event_name}.")


def process_alert(event_name, event_time, role_id):
    now = datetime.datetime.now(datetime.timezone.utc)
    warn_time = event_time - datetime.timedelta(minutes=WARNING_MINUTES)
    wait_seconds = (warn_time - now).total_seconds()

    if wait_seconds > 0:
        print(f"Event found: {event_name}. Waiting {wait_seconds / 60:.1f} minutes to send alert...")
        time.sleep(wait_seconds)
        send_alert(event_name, event_time, role_id)
    elif wait_seconds > -300:
        print(f"Slightly late for {event_name}. Sending immediately.")
        send_alert(event_name, event_time, role_id)

def main():
    if not WEBHOOK_URL:
        print("Error: Webhook URL missing.")
        return

    now = datetime.datetime.now(datetime.timezone.utc)

    # 1. DAILY SCHEDULE
    if now.hour == 12 or (now.hour == 13 and now.minute < 30):
        print(f"It is {now.strftime('%H:%M')} UTC. Sending Daily Schedule...")
        send_daily_schedule()

    # 2. ALERTS (Max lookahead 100 mins handles GitHub lag up to 1 hr)
    max_lookahead = 100 * 60

    # --- Check Event 1 (18:30 UTC) ---
    next_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)
    seconds_until_1 = (next_1 - now).total_seconds()

    # 18:30 is bottom of the hour -> Use 35 min threshold
    if 35 * 60 < seconds_until_1 <= max_lookahead:
        process_alert("Bear Trap 1", next_1, ROLE_ID_1)

    # --- Check Event 2 (05:00 UTC) ---
    next_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)
    seconds_until_2 = (next_2 - now).total_seconds()

    # 05:00 is top of the hour -> Use 10 min threshold
    if 10 * 60 < seconds_until_2 <= max_lookahead:
        process_alert("Bear Trap 2", next_2, ROLE_ID_2)

    # --- Check Event 3 (23:00 UTC) ---
    next_3 = get_next_event_time(START_DATE_3, INTERVAL_HOURS)
    seconds_until_3 = (next_3 - now).total_seconds()

    # 23:00 is top of the hour -> Use 10 min threshold
    if 10 * 60 < seconds_until_3 <= max_lookahead:
        process_alert("Bear Trap 3", next_3, ROLE_ID_3)

if __name__ == "__main__":
    main()