import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

# REAL World Cup fixture IDs (from validated schedule source)
FIXTURES = [
    66456904, 66456906, 66456916,
    66456940, 66456918, 66456928,
    66456930, 66456942, 66457070,
    66456968
]


# -------------------------
# GET EVENTS
# -------------------------
def get_events(fixture_id):
    url = "https://v3.football.api-sports.io/fixtures/events"

    headers = {
        "x-apisports-key": API_KEY.strip()
    }

    params = {
        "fixture": fixture_id
    }

    r = requests.get(url, headers=headers, params=params)

    if r.status_code != 200:
        return []

    return r.json().get("response", [])


# -------------------------
# BUILD DATASET
# -------------------------
def build_dataset():
    rows = []

    for fixture_id in FIXTURES:

        print(f"Processing fixture {fixture_id}")

        events = get_events(fixture_id)

        for e in events:
            player = e.get("player", {}).get("name")
            team = e.get("team", {}).get("name")

            if not player:
                continue

            rows.append({
                "fixture_id": fixture_id,
                "player": player,
                "team": team,
                "event_type": e.get("type"),
                "minute": e.get("time", {}).get("elapsed")
            })

    return pd.DataFrame(rows)


# -------------------------
# SAVE
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/worldcup_events.csv"
    df.to_csv(path, index=False)

    print(df.head())
    print("Saved:", path)


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== WORLD CUP REAL PLAYER EVENT PIPELINE ===")

    df = build_dataset()

    if df.empty:
        print("No data returned")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
