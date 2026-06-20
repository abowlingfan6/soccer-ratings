import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

# Correct World Cup competition ID
LEAGUE_ID = 7902
SEASON = 2026


# -------------------------
# GET WORLD CUP FIXTURES
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

    return r.json().get("response", [])


# -------------------------
# GET TEAM STATS (RELIABLE LAYER)
# -------------------------
def get_team_stats(fixture_id):
    url = "https://v3.football.api-sports.io/fixtures/statistics"

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
# OPTIONAL: GET EVENTS (NOT RELIABLE FOR ALL MATCHES)
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
# BUILD DATASET (HYBRID)
# -------------------------
def build_dataset(fixtures):
    rows = []

    print(f"Fixtures found: {len(fixtures)}")

    # safety limit for GitHub Actions
    fixtures = fixtures[:10]

    for f in fixtures:
        fixture_id = f["fixture"]["id"]
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]

        print(f"Processing {home} vs {away}")

        # -------------------------
        # PRIMARY: TEAM STATS
        # -------------------------
        stats = get_team_stats(fixture_id)

        for team_block in stats:
            team = team_block["team"]["name"]

            stat_map = {
                s["type"]: s["value"]
                for s in team_block.get("statistics", [])
            }

            rows.append({
                "fixture_id": fixture_id,
                "home_team": home,
                "away_team": away,
                "team": team,
                "source": "team_stats",
                "shots": stat_map.get("Total Shots", 0),
                "shots_on_target": stat_map.get("Shots on Goal", 0),
                "possession": stat_map.get("Ball Possession", "0%")
            })

        # -------------------------
        # OPTIONAL: EVENTS (if available)
        # -------------------------
        events = get_events(fixture_id)

        for e in events:
            player = e.get("player", {}).get("name")
            if not player:
                continue

            rows.append({
                "fixture_id": fixture_id,
                "home_team": home,
                "away_team": away,
                "team": e.get("team", {}).get("name"),
                "player": player,
                "source": "event",
                "event_type": e.get("type"),
                "minute": e.get("time", {}).get("elapsed")
            })

    return pd.DataFrame(rows)


# -------------------------
# SAVE OUTPUT
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/worldcup_dataset.csv"
    df.to_csv(path, index=False)

    print("Saved:", path)
    print(df.head())


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== WORLD CUP HYBRID ANALYTICS BOT ===")

    fixtures = get_fixtures()

    if not fixtures:
        print("No fixtures found")
        return

    df = build_dataset(fixtures)

    if df.empty:
        print("No data collected")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()

