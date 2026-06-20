import os
import pandas as pd

# World Cup match IDs from schedule source
MATCHES = [
    66456904, 66456906, 66456916, 66456940,
    66456918, 66456928, 66456930
]


def get_mock_events(match_id):
    """
    Placeholder until we plug in a stats API per match.
    This ensures pipeline works end-to-end FIRST.
    """

    # Simulated structure (replaced later with real API stats)
    return [
        {"fixture_id": match_id, "player": "Player A", "team": "Team X", "event_type": "goal", "minute": 34},
        {"fixture_id": match_id, "player": "Player B", "team": "Team Y", "event_type": "yellowcard", "minute": 55},
    ]


def build_dataset():
    rows = []

    for m in MATCHES:
        events = get_mock_events(m)
        rows.extend(events)

    return pd.DataFrame(rows)


def save(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/worldcup_events.csv", index=False)
    print(df.head())
    print("Saved data/worldcup_events.csv")


def main():
    print("=== WORLD CUP PIPELINE (STABLE VERSION) ===")

    df = build_dataset()

    save(df)

    print("DONE")


if __name__ == "__main__":
    main()
