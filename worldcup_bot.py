import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")
MATCH_ID = 1264426


# -------------------------
# SAFE API CALL
# -------------------------
def safe_request(url, params):
    headers = {"x-apisports-key": API_KEY}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        print(f"{url} -> {r.status_code}")

        if r.status_code != 200:
            print(r.text[:200])
            return None

        return r.json()

    except Exception as e:
        print("Request failed:", e)
        return None


# -------------------------
# EVENTS
# -------------------------
def get_events():
    url = "https://v3.football.api-sports.io/fixtures/events"
    data = safe_request(url, {"fixture": MATCH_ID})

    if not data:
        return []

    return data.get("response", [])


# -------------------------
# STATS
# -------------------------
def get_stats():
    url = "https://v3.football.api-sports.io/fixtures/statistics"
    data = safe_request(url, {"fixture": MATCH_ID})

    if not data:
        return []

    return data.get("response", [])


# -------------------------
# LINEUPS
# -------------------------
def get_lineups():
    url = "https://v3.football.api-sports.io/fixtures/lineups"
    data = safe_request(url, {"fixture": MATCH_ID})

    if not data:
        return []

    return data.get("response", [])


# -------------------------
# SAFE SAVE FUNCTION
# -------------------------
def save_df(df, path):
    if df is None or df.empty:
        print(f"Skipping empty file: {path}")
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


# -------------------------
# BUILD EVENTS DATASET
# -------------------------
def build_events():
    rows = []

    for e in get_events():
        rows.append({
            "match_id": MATCH_ID,
            "player": e.get("player", {}).get("name"),
            "team": e.get("team", {}).get("name"),
            "type": e.get("type"),
            "detail": e.get("detail"),
            "minute": e.get("time", {}).get("elapsed")
        })

    return pd.DataFrame(rows)


# -------------------------
# BUILD STATS DATASET
# -------------------------
def build_stats():
    rows = []

    for team in get_stats():
        team_name = team.get("team", {}).get("name")

        for s in team.get("statistics", []):
            rows.append({
                "match_id": MATCH_ID,
                "team": team_name,
                "stat": s.get("type"),
                "value": s.get("value")
            })

    return pd.DataFrame(rows)


# -------------------------
# BUILD LINEUPS DATASET
# -------------------------
def build_lineups():
    rows = []

    for team in get_lineups():
        team_name = team.get("team", {}).get("name")

        for p in team.get("startXI", []):
            rows.append({
                "match_id": MATCH_ID,
                "team": team_name,
                "player": p.get("player", {}).get("name"),
                "position": p.get("player", {}).get("pos")
            })

    return pd.DataFrame(rows)


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== STABLE WORLD CUP DATA PIPELINE ===")

    events_df = build_events()
    stats_df = build_stats()
    lineups_df = build_lineups()

    # SAVE ONLY IF VALID
    save_df(events_df, "data/match_events.csv")
    save_df(stats_df, "data/match_stats.csv")
    save_df(lineups_df, "data/match_lineups.csv")

    print("DONE")


if __name__ == "__main__":
    main()
