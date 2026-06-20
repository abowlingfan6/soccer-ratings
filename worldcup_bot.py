import requests
import pandas as pd
import os

MATCH_ID = 15186710
BASE_URL = f"https://api.sofascore.com/api/v1/event/{MATCH_ID}"


# -----------------------------
# SAFE FETCH (handles 403/empty)
# -----------------------------
def fetch(endpoint):
    url = f"{BASE_URL}/{endpoint}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.sofascore.com/"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Fetching {url} -> Status {r.status_code}")

        if r.status_code != 200:
            return {}

        return r.json()

    except Exception as e:
        print("Fetch error:", e)
        return {}


# -----------------------------
# GET INCIDENTS
# -----------------------------
def get_incidents():
    data = fetch("incidents")
    return data if isinstance(data, dict) else {}


# -----------------------------
# EXTRACT PLAYER EVENTS
# -----------------------------
def build_players(incidents):
    players = {}

    if not incidents or "incidents" not in incidents:
        print("No incidents found")
        return pd.DataFrame(columns=["player", "goals", "cards"])

    for inc in incidents.get("incidents", []):
        name = inc.get("playerName")
        event = inc.get("incidentType")

        if not name:
            continue

        if name not in players:
            players[name] = {
                "player": name,
                "goals": 0,
                "cards": 0
            }

        if event == "goal":
            players[name]["goals"] += 1

        if event in ["yellowcard", "redcard"]:
            players[name]["cards"] += 1

    return pd.DataFrame(players.values())


# -----------------------------
# SIMPLE RATING MODEL
# -----------------------------
def calculate_rating(row):
    return (
        6.0 +
        (1.5 * row["goals"]) -
        (0.5 * row["cards"])
    )


# -----------------------------
# SAVE OUTPUT
# -----------------------------
def save(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/match_ratings.csv", index=False)


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("=== SINGLE MATCH BOT STARTED ===")

    incidents = get_incidents()

    players = build_players(incidents)

    print("Players extracted:")
    print(players)

    if players.empty:
        print("No data found — exiting safely")
        return

    players["rating"] = players.apply(calculate_rating, axis=1)

    save(players)

    print("DONE — CSV CREATED")


if __name__ == "__main__":
    main()
