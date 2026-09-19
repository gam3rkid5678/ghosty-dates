import os
import json
import datetime
import time
import random
import requests

# Load the master schedule entries
with open("times.json", "r") as f:
    time_slots = json.load(f)

# Persistent file-based lock tracker to permanently prevent double-posting
HISTORY_FILE = "sent_history.json"

def load_sent_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                # If the cache file belongs to a previous date, wipe it for a fresh day
                if data.get("date") == datetime.date.today().isoformat():
                    return set(data.get("slots", []))
        except Exception:
            pass
    return set()

def save_sent_history(sent_set):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump({
                "date": datetime.date.today().isoformat(),
                "slots": list(sent_set)
            }, f)
    except Exception as e:
        print(f"History logging exception: {e}")

sent_today = load_sent_history()

# Color options list (Magenta, Cyan, and Blurple decimal codes)
NOTIF_COLORS = [15732731, 6128894, 5793266]

print("Ghosty Precision Engine Active. Multi-Cushion Overlap Protection Engaged...")

boot_time = datetime.datetime.now(datetime.timezone.utc)
# Server stays awake for exactly 28 minutes to safely exit before the next cron fires
end_shift_time = boot_time + datetime.timedelta(minutes=28)

while datetime.datetime.now(datetime.timezone.utc) < end_shift_time:
    now = datetime.datetime.now(datetime.timezone.utc)
    sent_today = load_sent_history()  # Always read fresh state to block parallel runs
    
    # ⏱️ RETROACTIVE LOOK-BACKWARD NET: Scans 5 minutes backward up to 2 minutes forward
    possible_times = []
    for offset in range(-5, 3):  # Checks -5, -4, -3, -2, -1, 0, 1, and 2 minutes relative to now
        check_time = now + datetime.timedelta(minutes=offset)
        possible_times.append(check_time.strftime("%H:%M"))

    # Locate the first valid scheduled slot inside our safety window
    target_time_str = None
    for t_str in possible_times:
        if t_str in time_slots and t_str not in sent_today:
            target_time_str = t_str
            break

    if target_time_str:
        # If the discovered slot is in the future, sleep precisely until its minute arrives
        time_now_str = now.strftime("%H:%M")
        if target_time_str > time_now_str:
            print(f"[{now.strftime('%X')}] Found upcoming slot {target_time_str}. Holding precision loop...")
            while datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M") < target_time_str:
                time.sleep(1)
            now = datetime.datetime.now(datetime.timezone.utc)

        raw_message = time_slots[target_time_str]
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        
        if webhook_url:
            # 🎯 SPECIAL MIDNIGHT CROSSOVER: 23:59 Magic Hour automatically chains into 00:00 Daily Collection
            if target_time_str == "23:59":
                payload_magic = {
                    "content": raw_message,
                    "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                }
                requests.post(webhook_url, json=payload_magic)
                print(f"[{now.strftime('%X')}] Magic Hour text alert posted successfully.")
                sent_today.add("23:59")
                save_sent_history(sent_today)
                
                print("Holding script connection to execute midnight transition roll...")
                time.sleep(60)
                
                if "00:00" in time_slots and "00:00" not in sent_today:
                    payload_daily = {
                        "content": time_slots["00:00"],
                        "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                    }
                    requests.post(webhook_url, json=payload_daily)
                    print(f"[{datetime.datetime.now(datetime.timezone.utc).strftime('%X')}] Midnight Daily text alert posted successfully.")
                    sent_today.add("00:00")
                    save_sent_history(sent_today)
                
                time.sleep(5)
                
            elif target_time_str == "00:00" and "00:00" in sent_today:
                pass
            
            # 🎨 AUTOMATIC EMBED CARDS: Regular schedule targets get formatted wide layouts
            else:
                chosen_color = random.choice(NOTIF_COLORS)
                role_ping = "<@&1464434655829692577>"
                
                header_title = raw_message.replace(role_ping, "").strip()
                
                # 🎯 VERIFIED DIRECT LINK: Imgur CDN address perfectly locked onto line 108
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
                save_sent_history(sent_today)
                time.sleep(65)
        else:
            print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
            break
            
    time.sleep(2)

print("Interval loop complete. Disconnecting safely.")
