import pandas as pd

# You can replace this with any match or team page later
MATCH_URL = "https://fbref.com/en/matches/3c1e3816/Mexico-South-Africa-June-11-2026-World-Cup"


def get_tables():
    return pd.read_html(MATCH_URL)


def find_player_table(tables):
    for t in tables:
        cols = [str(c).lower() for c in t.columns]
        if any("player" in c for c in cols):
            return t
    return None


def main():
    tables = get_tables()
    print(f"Tables found: {len(tables)}")

    player_table = find_player_table(tables)

    if player_table is None:
        print("No player table found")
        return

    player_table.columns = [str(c).strip() for c in player_table.columns]

    player_table.to_csv("data/fbref_players.csv", index=False)

    print("Saved fbref_players.csv")


if __name__ == "__main__":
    main()
