import os
import json
import datetime
import time
import random
import requests
import subprocess

# 🔒 THE INSTANT EXIT LOCK: Checks if another active runner is already handling the timeline
def check_active_runners():
    try:
        repo = os.environ.get("GITHUB_REPOSITORY")
        token = os.environ.get("GITHUB_TOKEN")
        if repo and token:
            url = f"https://github.com{repo}/actions/runs?status=in_progress"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
            res = requests.get(url, headers=headers).json()
            runs = [r for r in res.get("workflow_runs", []) if r.get("name") == "Ghosty Precision Single-Interval Scheduler"]
            # If there is more than 1 in_progress run (this one included), exit instantly!
            if len(runs) > 1:
                print("🚨 Secondary runner detected! Exiting to prevent overlap loops.")
                return True
    except Exception as e:
        print(f"Runner check error: {e}")
    return False

if check_active_runners():
    os._exit(0)

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

# 🎯 FIXED: Color options list (Magenta, Cyan, and Blurple decimal codes)
NOTIF_COLORS = [16711935, 65535, 5793266] 

print("Ghosty Precision Engine Active. Forward-Only Firewall Live...")

boot_time = datetime.datetime.now(datetime.timezone.utc)
end_shift_time = boot_time + datetime.timedelta(minutes=13)

while datetime.datetime.now(datetime.timezone.utc) < end_shift_time:
    now = datetime.datetime.now(datetime.timezone.utc)
    sent_today = load_sent_history()
    
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
                
                # 🎯 FIXED: Corrected Imgur link path
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
