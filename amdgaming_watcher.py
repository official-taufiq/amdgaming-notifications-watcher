import hashlib
import os
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SESSION_COOKIE = os.getenv("AMDGAMING_COOKIE", "")
STATE_FILE = "seen_ids.txt"

TARGET_SOURCES = [
    {
        "name": "AMD Gaming Feed",
        "url": "https://www.amdgaming.com/",
    },
    {
        "name": "AMD Gaming Promotions",
        "url": "https://www.amdgaming.com/promotions",
    },
]


def send_discord_notification(source_name: str, title: str, link: str):
    payload = {
        "username": "AMD Gaming Alert",
        "avatar_url": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/amd.png",
        "embeds": [
            {
                "title": title,
                "url": link,
                "color": 0xED1C24,  # AMD Red
                "fields": [
                    {"name": "Source", "value": source_name, "inline": True},
                    {"name": "Link", "value": f"[Open Page]({link})", "inline": True},
                ],
                "footer": {"text": "amdgaming.com monitor"},
            }
        ],
    }
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    if resp.status_code == 204:
        print(f"[{source_name}] Sent: {title}")
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


def parse_page_items(url: str, session: requests.Session) -> list[dict]:
    res = session.get(url, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    found_items = []

    # Extracts links that point to community posts, announcements, missions, or promotions
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        title = a.get_text(strip=True)

        if not title or len(title) < 5:
            continue

        # Filter out generic navigation elements
        if any(
            ignore in title.lower()
            for ignore in [
                "login",
                "sign up",
                "register",
                "privacy",
                "terms",
                "cookie",
                "home",
            ]
        ):
            continue

        full_url = href if href.startswith("http") else f"https://www.amdgaming.com{href}"

        # Generate a stable fingerprint using URL + Title
        item_id = hashlib.sha256(f"{full_url}:{title}".encode("utf-8")).hexdigest()[:16]

        found_items.append({"id": item_id, "title": title, "url": full_url})

    return found_items


def check_all_sources():
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing.")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    if SESSION_COOKIE:
        session.headers["Cookie"] = SESSION_COOKIE

    seen_ids = load_seen_ids()
    new_seen = set(seen_ids)

    # First run bootstrap: if state file is completely empty, populate without spamming Discord
    is_initial_run = len(seen_ids) == 0

    for source in TARGET_SOURCES:
        try:
            items = parse_page_items(source["url"], session)
            for item in items:
                item_id = item["id"]
                if item_id not in seen_ids:
                    if not is_initial_run:
                        send_discord_notification(source["name"], item["title"], item["url"])
                    new_seen.add(item_id)
        except Exception as e:
            print(f"Error checking {source['name']}: {e}")

    save_seen_ids(new_seen)
    if is_initial_run:
        print("Initial run complete: indexed existing items without sending alerts.")


if __name__ == "__main__":
    check_all_sources()
