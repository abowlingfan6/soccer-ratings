import pandas as pd
import os

# -------------------------
# SAFE LOADER
# -------------------------
def load(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


events = load("data/match_events.csv")
lineups = load("data/match_lineups.csv")
fbref = load("data/fbref_players.csv")


if events.empty:
    print("No event data — exiting safely")
    exit()

# -------------------------
# POSITION MAP
# -------------------------
pos_map = {}

for _, r in lineups.iterrows():
    if "player" in r and "position" in r:
        pos_map[r["player"]] = r["position"]


def get_pos(p):
    return pos_map.get(p, "MF")


# -------------------------
# EVENT MODEL (BASE PERFORMANCE)
# -------------------------
def event_score(row):
    t = str(row.get("type", "")).lower()
    d = str(row.get("detail", "")).lower()

    score = 0

    if t == "goal":
        score += 1.0 if "penalty" not in d else 0.75

    if "assist" in t:
        score += 0.7

    if "yellow" in d:
        score -= 0.3

    if "red" in d:
        score -= 1.0

    return score


events["event_score"] = events.apply(event_score, axis=1)

player_base = events.groupby("player")["event_score"].sum().reset_index()


# -------------------------
# FBREF ENRICHMENT (IF AVAILABLE)
# -------------------------
fbref_bonus = {}

if not fbref.empty:
    for _, r in fbref.iterrows():
        player = str(r.get("Player", ""))

        shots = r.get("Sh", 0) if "Sh" in r else 0
        goals = r.get("Gls", 0) if "Gls" in r else 0
        ast = r.get("Ast", 0) if "Ast" in r else 0

        try:
            fbref_bonus[player] = (
                float(goals) * 1.0 +
                float(ast) * 0.7 +
                float(shots) * 0.1
            )
        except:
            fbref_bonus[player] = 0


# -------------------------
# RATING ENGINE (YOUR 6.0 SYSTEM)
# -------------------------
results = []

for _, r in player_base.iterrows():

    player = r["player"]
    base = 6.0

    event = r["event_score"]
    fb = fbref_bonus.get(player, 0)

    pos = get_pos(player)

    # POSITION WEIGHTING (YOUR MODEL)
    if pos == "GK":
        rating = base + event * 1.1 + fb * 0.5

    elif pos == "DF":
        rating = base + event * 1.2 + fb * 0.8

    elif pos == "MF":
        rating = base + event * 1.3 + fb * 1.0

    elif pos == "FW":
        rating = base + event * 1.5 + fb * 1.2

    else:
        rating = base + event + fb

    results.append({
        "player": player,
        "position": pos,
        "rating": round(rating, 2)
    })


out = pd.DataFrame(results).sort_values("rating", ascending=False)

os.makedirs("data", exist_ok=True)
out.to_csv("data/player_ratings.csv", index=False)

print(out)
print("\nSaved player_ratings.csv")
