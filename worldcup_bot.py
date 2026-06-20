import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

# FIFA World Cup (API-Football)
LEAGUE_ID = 1
SEASON = 2026


# -------------------------
# GET FIXTURES (REAL MATCHES)
# -------------------------
def get_fixtures():
    url = "https://v3.football.api-sports.io/fixtures"

    headers = {
        "x-apisports-key": API_KEY.strip()
    }

    params = {
        "league": LEAGUE_ID,
        "season": SEASON
    }

    r = requests.get(url, headers=headers, params=params)

    print("Fixtures status:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return []

    data = r.json()
    return data.get("response", [])


# -------------------------
# GET MATCH EVENTS (PLAYERS)
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
# BUILD PLAYER EVENT DATASET
# -------------------------
def build_dataset(fixtures):
    rows = []

    print(f"Total fixtures found: {len(fixtures)}")

    # limit for GitHub Actions safety
    fixtures = fixtures[:10]

    for f in fixtures:
        fixture_id = f["fixture"]["id"]

        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]

        print(f"Processing: {home} vs {away}")

        events = get_events(fixture_id)

        for e in events:
            player = e.get("player", {}).get("name")
            team = e.get("team", {}).get("name")

            # skip invalid rows
            if not player:
                continue

            rows.append({
                "fixture_id": fixture_id,
                "home_team": home,
                "away_team": away,
                "player": player,
                "team": team,
                "event_type": e.get("type"),
                "minute": e.get("time", {}).get("elapsed")
            })

    return pd.DataFrame(rows)


# -------------------------
# SAVE CSV
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/worldcup_events.csv"
    df.to_csv(path, index=False)

    print("Saved:", path)
    print(df.head())


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== WORLD CUP PLAYER EVENT BOT ===")

    fixtures = get_fixtures()

    if not fixtures:
        print("No fixtures returned — check league/season")
        return

    df = build_dataset(fixtures)

    if df.empty:
        print("No player event data found")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
