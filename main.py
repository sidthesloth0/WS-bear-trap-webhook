import requests
import datetime
import os
import time

# configuration
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
INTERVAL_HOURS = 48
WARNING_MINUTES = 3

# event 1
START_DATE_1 = datetime.datetime(2026, 3, 3, 18, 30, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_1 = "1464765731336880222"

# event 2
START_DATE_2 = datetime.datetime(2026, 3, 4, 6, 0, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_2 = "1464766114981478430"
# ---------------------------------------------------------

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
    ts_1 = int(next_event_1.timestamp())
    ts_2 = int(next_event_2.timestamp())

    payload = {
        "content": "📢 **Daily Schedule Update**",
        "embeds": [{
            "title": "Upcoming Bear Traps in the next 48-Hours",
            "description": "Here is the schedule for the upcoming Bear Traps:",
            "color": 5814783,
            "fields": [
                {"name": "Bear Trap 1", "value": f"<t:{ts_1}:F>\n(<t:{ts_1}:R>)", "inline": False},
                {"name": "Bear Trap 2", "value": f"<t:{ts_2}:F>\n(<t:{ts_2}:R>)", "inline": False}
            ]
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
    print("✅ Daily schedule sent.")

def send_alert(event_name, event_time, role_id):
    ts = int(event_time.timestamp())
    payload = {
        "content": f"🚨 **HEADS UP <@&{role_id}>!**",
        "embeds": [{
            "title": f"⚔️ {event_name} is Starting in {WARNING_MINUTES} minutes!",
            "description": f"Prepare yourselves! The event begins <t:{ts}:R> at <t:{ts}:t>!",
            "color": 15548997,  # Red
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
    print(f"✅ Alert sent for {event_name}.")

def process_alert(event_name, event_time, role_id):
    now = datetime.datetime.now(datetime.timezone.utc)

    # Target time is (Event Time - Warning Minutes)
    warn_time = event_time - datetime.timedelta(minutes=WARNING_MINUTES)

    # Calculate how long to wait
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

    # 2. ALERTS
    # Max Lookahead: 100 Minutes (Allows script to see events in the next hour)
    max_lookahead = 100 * 60

    # --- Check Event 1 ---
    next_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)
    seconds_until_1 = (next_1 - now).total_seconds()

    # SMART LOGIC 1:
    # Event is at XX:00. We rely on the CURRENT hour's script (e.g. 5:00 run for 6:00 event).
    # We set a LOW threshold (10 mins) so even if it lags to 5:45, it still catches it.
    if 10 * 60 < seconds_until_1 <= max_lookahead:
        process_alert("Bear Trap 1", next_1, ROLE_ID_1)

    # --- Check Event 2 ---
    next_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)
    seconds_until_2 = (next_2 - now).total_seconds()

    # event is at XX:30. We rely on the previous hour's script (e.g. 17:00 run for 18:30 event)
    # set a high threshold (45 mins) so the 18:00 run ignores it, preventing double ping.
    if 45 * 60 < seconds_until_2 <= max_lookahead:
        process_alert("Bear Trap 2", next_2, ROLE_ID_2)

if __name__ == "__main__":
    main()