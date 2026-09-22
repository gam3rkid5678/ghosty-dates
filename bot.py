import os
import json
import datetime
import time
import random
import requests
import subprocess

with open("times.json", "r") as f:
    time_slots = json.load(f)

HISTORY_FILE = "sent_history.json"

def load_sent_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
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
        
        subprocess.run(["git", "config", "--global", "user.name", "Ghosty Bot"], check=True)
        subprocess.run(["git", "--global", "user.email", "bot@ghosty.live"], check=True)
        subprocess.run(["git", "config", "pull.rebase", "true"], check=True)
        
        subprocess.run(["git", "add", HISTORY_FILE], check=True)
        
        commit_res = subprocess.run(["git", "commit", "-m", "chore: update drop history [skip ci]"], capture_output=True, text=True)
        if "nothing to commit" not in commit_res.stdout:
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("History successfully synchronized with branch.")
            
    except Exception as e:
        print(f"History syncing exception: {e}")

sent_today = load_sent_history()

# 🎯 RESTORED: Your exact notification color options list
NOTIF_COLORS = [16711935, 65535, 5793266]

print("Ghosty 1-Hour Shift Engine Active. Forward-Only Tracking Live...")

boot_time = datetime.datetime.now(datetime.timezone.utc)
# 🎯 55-MINUTE SHIFT: Safely tracks the timeline continuously on a single thread and reboots safely
end_shift_time = boot_time + datetime.timedelta(minutes=55)

while datetime.datetime.now(datetime.timezone.utc) < end_shift_time:
    now = datetime.datetime.now(datetime.timezone.utc)
    sent_today = load_sent_history()
    
    # ⏱️ FORWARD-ONLY FIREWALL: Strictly checks the current minute and 1 minute forward
    possible_times = []
    for offset in range(0, 2):
        check_time = now + datetime.timedelta(minutes=offset)
        possible_times.append(check_time.strftime("%H:%M"))

    target_time_str = None
    for t_str in possible_times:
        if t_str in time_slots and t_str not in sent_today:
            target_time_str = t_str
            break

    if target_time_str:
        time_now_str = now.strftime("%H:%M")
        if target_time_str > time_now_str:
            while datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M") < target_time_str:
                time.sleep(1)
            now = datetime.datetime.now(datetime.timezone.utc)

        raw_message = time_slots[target_time_str]
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        
        if webhook_url:
            if target_time_str == "23:59":
                payload_magic = {
                    "content": raw_message,
                    "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                }
                requests.post(webhook_url, json=payload_magic)
                sent_today.add("23:59")
                save_sent_history(sent_today)
                time.sleep(60)
                
                if "00:00" in time_slots and "00:00" not in sent_today:
                    payload_daily = {
                        "content": time_slots["00:00"],
                        "allowed_mentions": {"parse": ["roles", "users", "everyone"]}
                    }
                    requests.post(webhook_url, json=payload_daily)
                    sent_today.add("00:00")
                    save_sent_history(sent_today)
                time.sleep(5)
                
            elif target_time_str == "00:00":
                pass
            
            else:
                chosen_color = random.choice(NOTIF_COLORS)
                role_ping = "<@&1464434655829692577>"
                
                header_title = raw_message.replace(role_ping, "").strip()
                
                # 🎯 RESTORED: Direct animated GIF url path link
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
                sent_today.add(target_time_str)
                save_sent_history(sent_today)
                time.sleep(65)
        else:
            break
            
    time.sleep(2)

print("Shift tracking cycle complete.")
