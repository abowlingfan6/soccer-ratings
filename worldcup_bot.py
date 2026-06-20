import os
import requests

API_KEY = os.environ.get("API_FOOTBALL_KEY")

url = "https://v3.football.api-sports.io/fixtures"

headers = {
    "x-apisports-key": API_KEY.strip()
}

params = {
    "date": "2026-06-11",
    "search": "Mexico"
}

r = requests.get(url, headers=headers, params=params)

print(r.status_code)
print(r.json())


# -------------------------
# FETCH EVENTS
# -------------------------
def fetch_events():
    url = "https://v3.football.api-sports.io/fixtures/events"

    headers = {
        "x-apisports-key": API_KEY.strip()
    }

    params = {
        "fixture": MATCH_ID
    }

    r = requests.get(url, headers=headers, params=params)

    print("Status:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return None

    return r.json()


# -------------------------
# BUILD CLEAN CSV DATA
# -------------------------
def build_df(data):
    rows = []

    if not data or "response" not in data:
        return pd.DataFrame(columns=[
            "player", "team", "event_type", "time"
        ])

    for item in data["response"]:
        rows.append({
            "player": item.get("player", {}).get("name"),
            "team": item.get("team", {}).get("name"),
            "event_type": item.get("type"),
            "time": item.get("time", {}).get("elapsed")
        })

    return pd.DataFrame(rows)


# -------------------------
# SAVE CSV
# -------------------------
def save(df):
    os.makedirs("data", exist_ok=True)

    path = "data/match_events.csv"
    df.to_csv(path, index=False)

    print("Saved:", path)
    print(df.head())


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== MATCH DATA EXPORT BOT ===")

    data = fetch_events()

    df = build_df(data)

    if df.empty:
        print("No data returned — check API or fixture ID")
        return

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
