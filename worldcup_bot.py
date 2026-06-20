import requests
import pandas as pd
import os

API_KEY = os.environ.get("API_FOOTBALL_KEY")

MATCH_ID = 15186710  # we will convert this later if needed


# -------------------------
# FETCH FROM API-FOOTBALL
# -------------------------
def fetch_match_stats():
    url = "https://v3.football.api-sports.io/fixtures/statistics"

    headers = {
        "x-apisports-key": API_KEY
    }

    params = {
        "fixture": MATCH_ID
    }

    r = requests.get(url, headers=headers, params=params)

    print("Status:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return {}

    return r.json()


# -------------------------
# SIMPLE PLAYER MODEL (TEAM-LEVEL FIRST)
# -------------------------
def build_team_stats(data):
    rows = []

    if "response" not in data:
        return pd.DataFrame()

    for team_block in data["response"]:
        team_name = team_block["team"]["name"]

        stats = {s["type"]: s["value"] for s in team_block["statistics"]}

        rows.append({
            "team": team_name,
            "shots_on_goal": stats.get("Shots on Goal", 0),
            "shots_total": stats.get("Total Shots", 0),
            "possession": stats.get("Ball Possession", "0%")
        })

    return pd.DataFrame(rows)


# -------------------------
# SIMPLE RATING (TEAM VERSION FIRST)
# -------------------------
def calculate_rating(row):
    shots = float(row["shots_on_goal"] or 0)
    total = float(row["shots_total"] or 0)

    return 6.0 + (0.2 * shots) + (0.05 * total)


# -------------------------
# SAVE
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/match_ratings.csv", index=False)


# -------------------------
# MAIN
# -------------------------
def main():
    print("STARTING API-FOOTBALL BOT")

    data = fetch_match_stats()

    df = build_team_stats(data)

    print(df)

    if df.empty:
        print("No data returned")
        return

    df["rating"] = df.apply(calculate_rating, axis=1)

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
