import pandas as pd
import os


# -------------------------
# SAFE CSV LOADER
# -------------------------
def safe_read(path):
    if not os.path.exists(path):
        print(f"Missing file: {path}")
        return pd.DataFrame()

    if os.path.getsize(path) == 0:
        print(f"Empty file skipped: {path}")
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Failed reading {path}: {e}")
        return pd.DataFrame()


# -------------------------
# LOAD DATA SAFELY
# -------------------------
events = safe_read("data/match_events.csv")
stats = safe_read("data/match_stats.csv")
lineups = safe_read("data/match_lineups.csv")


# -------------------------
# STOP IF NO DATA
# -------------------------
if events.empty:
    print("No event data — stopping rating engine safely")
    exit()


# -------------------------
# POSITION MAP
# -------------------------
pos_map = {}

for _, r in lineups.iterrows():
    if "player" in r and "position" in r:
        pos_map[r["player"]] = r["position"]


def get_pos(player):
    return pos_map.get(player, "MF")


# -------------------------
# EVENT SCORE (YOUR SYSTEM STARTS HERE)
# -------------------------
def score_event(row):
    t = str(row.get("type", "")).lower()
    d = str(row.get("detail", "")).lower()

    score = 0

    if t == "goal":
        score += 1.0 if "penalty" not in d else 0.75

    if "subst" in t:
        score += 0.1

    if "yellow" in d:
        score -= 0.3

    if "red" in d:
        score -= 1.0

    return score


events["score"] = events.apply(score_event, axis=1)


# -------------------------
# PLAYER TOTALS
# -------------------------
player_scores = events.groupby("player")["score"].sum().reset_index()


# -------------------------
# TEAM BONUS (ONLY IF STATS EXISTS)
# -------------------------
team_bonus = {}

if not stats.empty:
    for _, r in stats.iterrows():
        if "possession" in str(r.get("stat", "")).lower():
            try:
                v = float(str(r.get("value", "0")).replace("%", ""))
                team_bonus[r.get("team")] = (v - 50) * 0.01
            except:
                pass


# -------------------------
# BUILD RATINGS
# -------------------------
rows = []

for _, r in player_scores.iterrows():

    player = r["player"]
    base = 6.0
    score = r["score"]

    pos = get_pos(player)

    team = events[events["player"] == player]["team"].iloc[0] if not events.empty else None
    bonus = team_bonus.get(team, 0)

    if pos == "DF":
        rating = base + score * 1.2 + bonus
    elif pos == "FW":
        rating = base + score * 1.5 + bonus
    elif pos == "MF":
        rating = base + score * 1.3 + bonus
    elif pos == "GK":
        rating = base + score * 1.1 + bonus
    else:
        rating = base + score + bonus

    rows.append({
        "player": player,
        "position": pos,
        "rating": round(rating, 2)
    })


out = pd.DataFrame(rows).sort_values("rating", ascending=False)

os.makedirs("data", exist_ok=True)
out.to_csv("data/player_ratings.csv", index=False)

print(out)
print("\nSaved: data/player_ratings.csv")
