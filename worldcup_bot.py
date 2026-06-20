import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

MATCH_ID = 1264426


# -------------------------
# GET MATCH EVENTS (API-SPORTS)
# -------------------------
def get_events(match_id):
    url = "https://v3.football.api-sports.io/fixtures/events"

    headers = {
        "x-apisports-key": API_KEY.strip()
    }

    params = {
        "fixture": match_id
    }

    r = requests.get(url, headers=headers, params=params)

    print("Status:", r.status_code)

    if r.status_code != 200:
        print(r.text[:300])
        return []

    return r.json().get("response", [])


# -------------------------
# BUILD DATASET
# -------------------------
def build():
    rows = []

    events = get_events(MATCH_ID)

    for e in events:
        player = e.get("player", {}).get("name")
        team = e.get("team", {}).get("name")
        event_type = e.get("type")
        detail = e.get("detail")
        minute = e.get("time", {}).get("elapsed")

        if not player:
            continue

        rows.append({
            "match_id": MATCH_ID,
            "player": player,
            "team": team,
            "event_type": event_type,
            "event_detail": detail,
            "minute": minute
        })

    return pd.DataFrame(rows)


# -------------------------
# SAVE CSV
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/match_events.csv"
    df.to_csv(path, index=False)

    print(df.head())
    print("Saved:", path)


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== API-FOOTBALL SINGLE MATCH PIPELINE ===")

    df = build()

    if df.empty:
        print("No data returned — check API key or fixture availability")
        return

    save(df)
    print("DONE")


if __name__ == "__main__":
    main()
