import pandas as pd
import os

print("Bot started!")

data = pd.DataFrame([
    {"player": "Test Player", "rating": 8.5}
])

os.makedirs("data", exist_ok=True)

data.to_csv(
    "data/worldcup_ratings.csv",
    index=False
)

print("CSV created successfully!")
