import requests
import pandas as pd
import os

MATCH_IDS = [
    15186710  # Mexico vs South Africa (example)
]


# -------------------------
# SOFASCORE EVENT FETCH
# -------------------------
def get_events(match_id):
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.sofascore.com/"
    }

    r = requests.get(url, headers=headers)

    print(f"Match {match_id} -> Status {r.status_code}")

    if r.status_code != 200:
        return []

    data = r.json()

    return data.get("incidents", [])


# -------------------------
# BUILD DATASET
# -------------------------
def build():
    rows = []

    for match_id in MATCH_IDS:
        incidents = get_events(match_id)

        for i in incidents:
            event_type = i.get("incidentType")
            player = i.get("player", {}).get("name")
            team = i.get("team", {}).get("name")
            minute = i.get("time")

            if not player:
                continue

            rows.append({
                "match_id": match_id,
                "player": player,
                "team": team,
                "event_type": event_type,
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
    print("=== SOFASCORE EVENT PIPELINE START ===")

    df = build()

    if df.empty:
        print("No data returned")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
