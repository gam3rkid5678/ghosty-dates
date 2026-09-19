import os
import json
import datetime
import time
import random
import requests

# Load the master schedule entries
with open("times.json", "r") as f:
    time_slots = json.load(f)

sent_today = set()

# Color options list (Magenta, Cyan, and Blurple decimal codes)
# Color options list (Magenta, Cyan, and Blurple decimal codes)
NOTIF_COLORS = [15418879, 53247, 5793266]

print("Ghosty Precision Engine Active. Isolated 30-Minute Shift Mode Engaged...")

boot_time = datetime.datetime.now(datetime.timezone.utc)
boot_minute = boot_time.minute

if boot_minute >= 30:
    print("Shift Lock: [Minutes :30 to :59 Block] Active.")
    start_bound = 30
    end_bound = 59
else:
    print("Shift Lock: [Minutes :00 to :29 Block] Active.")
    start_bound = 0
    end_bound = 29

end_shift_time = boot_time + datetime.timedelta(minutes=28)

while datetime.datetime.now(datetime.timezone.utc) < end_shift_time:
    now = datetime.datetime.now(datetime.timezone.utc)
    current_minute = now.minute
    current_time_str = now.strftime("%H:%M")

    target_time_str = None
    if current_time_str in time_slots and current_time_str not in sent_today:
        if start_bound <= current_minute <= end_bound:
            target_time_str = current_time_str

    if target_time_str:
        raw_message = time_slots[target_time_str]
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        
        if webhook_url:
            if target_time_str == "23:59":
                payload_magic = {
                    "content": raw_message,
                    "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                }
                requests.post(webhook_url, json=payload_magic)
                print(f"[{now.strftime('%X')}] Magic Hour text alert posted successfully.")
                sent_today.add("23:59")
                
                print("Holding script connection to execute midnight transition roll...")
                time.sleep(60)
                
                if "00:00" in time_slots:
                    payload_daily = {
                        "content": time_slots["00:00"],
                        "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                    }
                    requests.post(webhook_url, json=payload_daily)
                    print(f"[{datetime.datetime.now(datetime.timezone.utc).strftime('%X')}] Midnight Daily text alert posted successfully.")
                    sent_today.add("00:00")
                
                time.sleep(5)
                
            elif target_time_str == "00:00" and "00:00" in sent_today:
                pass
            
            else:
                chosen_color = random.choice(NOTIF_COLORS)
                role_ping = "<@&1464434655829692577>"
                
                header_title = raw_message.replace(role_ping, "").strip()
                gif_url = "https://i.imgur.com/peovWde.gif"
                
                payload = {
                    "content": role_ping,
                    "embeds": [
                        {
                            "title": header_title,
                            "color": chosen_color,
                            "image": {
                                "url": gif_url
                            }
                        }
                    ],
                    "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                }
                requests.post(webhook_url, json=payload)
                print(f"[{now.strftime('%X')}] Triggering automatic graphic embed layout for slot {target_time_str}")
                sent_today.add(target_time_str)
                time.sleep(65)
        else:
            print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
            break
            
    time.sleep(2)

print("Interval loop complete. Disconnecting safely.")
