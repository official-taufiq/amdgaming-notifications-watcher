import os
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SESSION_COOKIE = os.getenv("AMDGAMING_COOKIE", "")
STATE_FILE = "seen_ids.txt"


def send_discord_notification(title: str, description: str, link: str):
    payload = {
        "username": "AMD Gaming Alert",
        "avatar_url": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/amd.png",
        "embeds": [
            {
                "title": title,
                "description": description or "New update on amdgaming.com",
                "url": link,
                "color": 0xED1C24,
                "footer": {"text": "amdgaming.com notification monitor"},
            }
        ],
    }
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    if resp.status_code == 204:
        print(f"Delivered: {title}")
    else:
        print(f"Failed to post to Discord: {resp.status_code} {resp.text}")


def load_seen_ids() -> set[str]:
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen_ids(seen: set[str]):
    with open(STATE_FILE, "w") as f:
        for item in sorted(seen):
            f.write(f"{item}\n")


def check_updates():
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    if SESSION_COOKIE:
        headers["Cookie"] = SESSION_COOKIE

    # The notifications endpoint on amdgaming.com
    target_url = "https://amdgaming.com/api/notifications"

    try:
        res = requests.get(target_url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Fetch failed: {e}")
        return

    seen_ids = load_seen_ids()
    new_seen = set(seen_ids)

    items = data if isinstance(data, list) else data.get("notifications", [])

    for item in items:
        item_id = str(item.get("id"))
        if item_id and item_id not in seen_ids:
            title = item.get("title", "AMD Gaming Notification")
            desc = item.get("body") or item.get("description", "")
            link = item.get("url", "https://amdgaming.com")

            send_discord_notification(title, desc, link)
            new_seen.add(item_id)

    save_seen_ids(new_seen)


if __name__ == "__main__":
    check_updates()import os
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SESSION_COOKIE = os.getenv("AMDGAMING_COOKIE", "")
STATE_FILE = "seen_ids.txt"


def send_discord_notification(title: str, description: str, link: str):
    payload = {
        "username": "AMD Gaming Alert",
        "avatar_url": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/amd.png",
        "embeds": [
            {
                "title": title,
                "description": description or "New update on amdgaming.com",
                "url": link,
                "color": 0xED1C24,
                "footer": {"text": "amdgaming.com notification monitor"},
            }
        ],
    }
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    if resp.status_code == 204:
        print(f"Delivered: {title}")
    else:
        print(f"Failed to post to Discord: {resp.status_code} {resp.text}")


def load_seen_ids() -> set[str]:
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen_ids(seen: set[str]):
    with open(STATE_FILE, "w") as f:
        for item in sorted(seen):
            f.write(f"{item}\n")


def check_updates():
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    if SESSION_COOKIE:
        headers["Cookie"] = SESSION_COOKIE

    # The notifications endpoint on amdgaming.com
    target_url = "https://amdgaming.com/api/notifications"

    try:
        res = requests.get(target_url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Fetch failed: {e}")
        return

    seen_ids = load_seen_ids()
    new_seen = set(seen_ids)

    items = data if isinstance(data, list) else data.get("notifications", [])

    for item in items:
        item_id = str(item.get("id"))
        if item_id and item_id not in seen_ids:
            title = item.get("title", "AMD Gaming Notification")
            desc = item.get("body") or item.get("description", "")
            link = item.get("url", "https://amdgaming.com")

            send_discord_notification(title, desc, link)
            new_seen.add(item_id)

    save_seen_ids(new_seen)


if __name__ == "__main__":
    check_updates()
