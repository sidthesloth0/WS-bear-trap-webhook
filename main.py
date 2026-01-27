import requests
import datetime
import os
import time

# 1. CONFIGURATION
# ---------------------------------------------------------
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
INTERVAL_HOURS = 48
WARNING_MINUTES = 3  # Sends alert this many minutes before start

# --- EVENT 1 (e.g. Evening) ---
START_DATE_1 = datetime.datetime(2026, 1, 16, 18, 30, 0, tzinfo=datetime.timezone.utc)
ROLE_ID_1 = "1464765731336880222"

# --- EVENT 2 (e.g. Morning) ---
START_DATE_2 = datetime.datetime(2026, 1, 16, 5, 30, 0, tzinfo=datetime.timezone.utc)
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


# --- FUNCTION A: Sends the Daily Schedule (No Pings) ---
def send_daily_schedule():
    next_event_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)
    next_event_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)
    ts_1 = int(next_event_1.timestamp())
    ts_2 = int(next_event_2.timestamp())

    payload = {
        "content": "📢 **Daily Schedule Update**",
        "embeds": [{
            "title": "Upcoming 48-Hour Events",
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


# --- FUNCTION B: Sends the Alert (With Pings) ---
def send_alert(event_name, event_time, role_id):
    ts = int(event_time.timestamp())
    payload = {
        "content": f"🚨 **HEADS UP <@&{role_id}>!**",
        "embeds": [{
            "title": f"⚔️ {event_name} is Starting in 3 minutes!",
            "description": f"Prepare yourselves! The event begins in <t:{ts}:R> at <t:{ts}:t>!",
            "color": 15548997,  # Red
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
    print(f"✅ Alert sent for {event_name}.")


# --- FUNCTION C: Waits for the exact time, then calls Send Alert ---
def process_alert(event_name, event_time, role_id):
    now = datetime.datetime.now(datetime.timezone.utc)

    # Target time is (Event Time - Warning Minutes)
    warn_time = event_time - datetime.timedelta(minutes=WARNING_MINUTES)

    # Calculate how long to wait
    wait_seconds = (warn_time - now).total_seconds()

    if wait_seconds > 0:
        print(f"⏳ Event found: {event_name}. Waiting {wait_seconds / 60:.1f} minutes to send alert...")
        time.sleep(wait_seconds)  # Script pauses here
        send_alert(event_name, event_time, role_id)
    elif wait_seconds > -300:  # If we are late by less than 5 mins, send anyway
        print(f"⚠️ Slightly late for {event_name}. Sending immediately.")
        send_alert(event_name, event_time, role_id)


def main():
    if not WEBHOOK_URL:
        print("Error: Webhook URL missing.")
        return

    # Define 'now' clearly as a Datetime object
    now = datetime.datetime.now(datetime.timezone.utc)

    # ------------------------------------------------------
    # TASK 1: CHECK FOR DAILY SCHEDULE (Run only at 12:00 UTC)
    # ------------------------------------------------------
    if now.hour == 12:
        print("It is 12:00 UTC. Sending Daily Schedule...")
        send_daily_schedule()

    # ------------------------------------------------------
    # TASK 2: CHECK FOR ALERTS (Run Every Hour)
    # ------------------------------------------------------

    # MAX LIMIT: Look ahead 75 mins (e.g. 4:00 PM seeing a 5:05 PM event)
    max_lookahead = 75 * 60

    # MIN LIMIT: Ignore events in the next 15 mins.
    # If it's 5:00 PM and the event is at 5:05 PM, the script running
    # at 4:00 PM has *already* seen it and is waiting to send the alert.
    # skip here to prevent a double-ping.
    min_lookahead = 15 * 60

    # --- Check Event 1 ---
    next_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)

    # Calculate seconds difference (Datetime - Datetime = Timedelta)
    # We use .total_seconds() to convert that difference into a generic number (float)
    seconds_until_1 = (next_1 - now).total_seconds()

    # The fix: Only run if the time is within our specific window
    if min_lookahead < seconds_until_1 <= max_lookahead:
        process_alert("Bear Trap 1", next_1, ROLE_ID_1)

    # --- Check Event 2 ---
    next_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)
    seconds_until_2 = (next_2 - now).total_seconds()

    if min_lookahead < seconds_until_2 <= max_lookahead:
        process_alert("Bear Trap 2", next_2, ROLE_ID_2)


if __name__ == "__main__":
    main()