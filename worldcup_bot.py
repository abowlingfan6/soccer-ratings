import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

MATCH_ID = 1264426


# -------------------------
# EVENTS
# -------------------------
def get_events():
    url = "https://v3.football.api-sports.io/fixtures/events"
    headers = {"x-apisports-key": API_KEY}
    r = requests.get(url, headers=headers, params={"fixture": MATCH_ID})
    return r.json().get("response", [])


# -------------------------
# STATS (THIS IS WHAT YOUR EQUATION NEEDS)
# -------------------------
def get_stats():
    url = "https://v3.football.api-sports.io/fixtures/statistics"
    headers = {"x-apisports-key": API_KEY}
    r = requests.get(url, headers=headers, params={"fixture": MATCH_ID})
    return r.json().get("response", [])


# -------------------------
# LINEUPS (POSITION DATA)
# -------------------------
def get_lineups():
    url = "https://v3.football.api-sports.io/fixtures/lineups"
    headers = {"x-apisports-key": API_KEY}
    r = requests.get(url, headers=headers, params={"fixture": MATCH_ID})
    return r.json().get("response", [])


# -------------------------
# SAVE HELPERS
# -------------------------
def save(df, name):
    os.makedirs("data", exist_ok=True)
    path = f"data/{name}.csv"
    df.to_csv(path, index=False)
    print("Saved:", path)


# -------------------------
# MAIN BUILD
# -------------------------
def main():
    print("=== FULL DATA EXPORT FOR RATING ENGINE ===")

    # EVENTS
    events = []
    for e in get_events():
        events.append({
            "match_id": MATCH_ID,
            "player": e.get("player", {}).get("name"),
            "team": e.get("team", {}).get("name"),
            "type": e.get("type"),
            "detail": e.get("detail"),
            "minute": e.get("time", {}).get("elapsed")
        })
    save(pd.DataFrame(events), "match_events")

    # STATS
    stats = []
    for team in get_stats():
        team_name = team["team"]["name"]
        for s in team.get("statistics", []):
            stats.append({
                "match_id": MATCH_ID,
                "team": team_name,
                "stat": s["type"],
                "value": s["value"]
            })
    save(pd.DataFrame(stats), "match_stats")

    # LINEUPS
    lineup = []
    for team in get_lineups():
        team_name = team["team"]["name"]
        for p in team.get("startXI", []):
            lineup.append({
                "match_id": MATCH_ID,
                "team": team_name,
                "player": p["player"]["name"],
                "position": p["player"].get("pos")
            })
    save(pd.DataFrame(lineup), "match_lineups")

    print("DONE")


if __name__ == "__main__":
    main()
