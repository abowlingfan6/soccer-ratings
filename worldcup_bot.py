import os
import requests
import pandas as pd

API_KEY = os.environ.get("API_FOOTBALL_KEY")

# Use a known fixture (you can change later)
MATCH_ID = 15186710


# -------------------------
# SAFE API CALL
# -------------------------
def fetch_match():
    if not API_KEY:
        raise ValueError("Missing API_FOOTBALL_KEY")

    url = "https://v3.football.api-sports.io/fixtures/statistics"

    headers = {
        "x-apisports-key": API_KEY.strip()
    }

    params = {
        "fixture": MATCH_ID
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)

        print("Status:", r.status_code)

        if r.status_code != 200:
            print("Response:", r.text)
            return None

        return r.json()

    except Exception as e:
        print("Request failed:", e)
        return None


# -------------------------
# PARSE TEAM STATS SAFELY
# -------------------------
def parse(data):
    rows = []

    if not data or "response" not in data:
        print("No valid data returned")
        return pd.DataFrame(columns=["team", "shots_on_goal", "shots_total"])

    for team_block in data["response"]:
        team = team_block["team"]["name"]

        stats = {}
        for s in team_block.get("statistics", []):
            stats[s["type"]] = s["value"]

        rows.append({
            "team": team,
            "shots_on_goal": stats.get("Shots on Goal", 0) or 0,
            "shots_total": stats.get("Total Shots", 0) or 0
        })

    return pd.DataFrame(rows)


# -------------------------
# SIMPLE RATING MODEL
# -------------------------
def add_rating(df):
    if df.empty:
        return df

    df["rating"] = (
        6.0 +
        (0.2 * df["shots_on_goal"].astype(float)) +
        (0.05 * df["shots_total"].astype(float))
    )

    return df


# -------------------------
# SAVE SAFELY
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/match_ratings.csv"

    df.to_csv(path, index=False)

    print("Saved:", path)
    print("Exists:", os.path.exists(path))


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== SOCCER ANALYTICS BOT START ===")

    data = fetch_match()

    df = parse(data)

    print(df)

    df = add_rating(df)

    if df.empty:
        print("Empty dataframe — skipping save")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
