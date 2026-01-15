import requests
import datetime
import os

# 1. CONFIGURATION
# ---------------------------------------------------------
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
INTERVAL_HOURS = 48

# EVENT 1 ANCHOR: (Year, Month, Day, Hour, Minute, Second) in UTC
START_DATE_1 = datetime.datetime(2026, 1, 16, 18, 30, 0, tzinfo=datetime.timezone.utc)

# EVENT 2 ANCHOR: (Year, Month, Day, Hour, Minute, Second) in UTC
START_DATE_2 = datetime.datetime(2026, 1, 16, 5, 30, 0, tzinfo=datetime.timezone.utc)


# ---------------------------------------------------------

def get_next_event_time(start_date, interval_hours):
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - start_date
    hours_diff = diff.total_seconds() / 3600
    intervals_passed = int(hours_diff // interval_hours)
    next_interval_count = intervals_passed + 1
    next_event = start_date + datetime.timedelta(hours=next_interval_count * interval_hours)
    return next_event


def send_discord_message():
    # Calculate next times for BOTH events
    next_event_1 = get_next_event_time(START_DATE_1, INTERVAL_HOURS)
    next_event_2 = get_next_event_time(START_DATE_2, INTERVAL_HOURS)

    # Convert to Unix timestamps
    ts_1 = int(next_event_1.timestamp())
    ts_2 = int(next_event_2.timestamp())

    # Construct the JSON Payload with an Embed
    payload = {
        "content": "📢 **Bear Trap Schedule**",  # Message text outside the box
        "embeds": [
            {
                "title": "Bear Trap Schedule",
                "description": "Here are the times for the next two Bear Traps:",
                "color": 5814783,  # A nice blue/purple hex color
                "fields": [
                    {
                        "name": "Bear Trap 1",
                        "value": f"<t:{ts_1}:F>\n(<t:{ts_1}:R>)",  # Shows Date + "In X hours"
                        "inline": False
                    },
                    {
                        "name": "Bear Trap 2",
                        "value": f"<t:{ts_2}:F>\n(<t:{ts_2}:R>)",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Times are automatically displayed in your local timezone."
                }
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        print("Dual-event message sent successfully.")
    else:
        print(f"Failed: {response.status_code}, {response.text}")


if __name__ == "__main__":
    send_discord_message()