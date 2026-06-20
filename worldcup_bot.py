import requests
import pandas as pd
import os

MATCH_ID = 15186710
BASE = f"https://api.sofascore.com/api/v1/event/{MATCH_ID}"


def fetch(endpoint):
    url = f"{BASE}/{endpoint}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    print("Fetching:", url)
    print("Status:", r.status_code)

    try:
        return r.json()
    except:
        return {}


def get_incidents():
    data = fetch("incidents")
    return data


def extract_players(incidents):
    players = []

    if not incidents or "incidents" not in incidents:
        print("No incidents found")
        return pd.DataFrame(columns=["player", "event"])

    for inc in incidents["incidents"]:
        name = inc.get("playerName")
        event = inc.get("incidentType")

        if name:
            players.append({
                "player": name,
                "event": event
            })

    return pd.DataFrame(players)


def main():
    print("STARTING SOFASCORE TEST BOT")

    incidents = get_incidents()

    df = extract_players(incidents)

    print(df)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/worldcup_ratings.csv", index=False)

    print("DONE - CSV CREATED")


if __name__ == "__main__":
    main()
