import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

TEAM_ID = 8558
BASELINE = 1.1
TOP_N = 5


matches = pd.read_csv("Match.csv")
match_possesion = pd.read_csv("Match_Possesion.csv")
match_shots_on = pd.read_csv("Match_Shots_On.csv")
match_shots_off = pd.read_csv("Match_Shots_Off.csv")

team = pd.read_csv("Team.csv")
team_attr = pd.read_csv("Team_Attributes.csv")


# Points function
def pts(f, a):
    return 3 if f > a else 1 if f == a else 0


# Calculate points long format for TEAM_ID
matches["home_points"] = matches.apply(
    lambda r: pts(r.home_team_goal, r.away_team_goal), axis=1
)
matches["away_points"] = matches.apply(
    lambda r: pts(r.away_team_goal, r.home_team_goal), axis=1
)

home = matches[matches.home_team_api_id == TEAM_ID][
    ["home_team_api_id", "away_team_api_id", "home_points"]
]
home.columns = ["team_api_id", "opponent_team_api_id", "points"]
away = matches[matches.away_team_api_id == TEAM_ID][
    ["away_team_api_id", "home_team_api_id", "away_points"]
]
away.columns = ["team_api_id", "opponent_team_api_id", "points"]

df = pd.concat([home, away], ignore_index=True)
avg_pts = df.groupby("opponent_team_api_id")["points"].mean().reset_index()

# Add team names
our_team = team.loc[team.team_api_id == TEAM_ID, "team_long_name"].values[0]
avg_pts["team_api_id"] = TEAM_ID
avg_pts["team_long_name"] = our_team

avg_pts = avg_pts.merge(
    team[["team_api_id", "team_long_name"]],
    left_on="opponent_team_api_id",
    right_on="team_api_id",
    how="left",
    suffixes=("", "_opponent"),
)
df_final = avg_pts.sort_values("points", ascending=False).reset_index(
    drop=True
)

# Plot avg points
colors = [
    (
        "limegreen"
        if i < TOP_N
        else "crimson" if i >= len(df_final) - TOP_N else "black"
    )
    for i in range(len(df_final))
]
heights = [
    (p - BASELINE) if p >= BASELINE else (BASELINE - p)
    for p in df_final.points
]
bottoms = [BASELINE if p >= BASELINE else p for p in df_final.points]

plt.figure(figsize=(12, 6))
bars = plt.bar(
    df_final.team_long_name_opponent, heights, bottom=bottoms, color=colors
)
plt.axhline(BASELINE, color="black", linewidth=3)
plt.xticks([])
plt.yticks(
    np.arange(
        min(df_final.points.min(), BASELINE - 1),
        max(df_final.points.max(), BASELINE + 1) + 0.25,
        0.25,
    )
)
plt.grid(axis="y", linestyle=":", alpha=0.7)
plt.ylabel("Avg Points")
plt.title(f"Avg Points by {our_team} vs Opponents")

for i, (bar, name, p) in enumerate(
    zip(bars, df_final.team_long_name_opponent, df_final.points)
):
    x = bar.get_x() + bar.get_width() / 2
    if p >= BASELINE:
        plt.text(
            x,
            BASELINE - 0.05,
            name,
            ha="right",
            va="top",
            rotation=45,
            color=colors[i],
            fontsize=9,
        )
    else:
        plt.text(
            x,
            bottoms[i] + heights[i] + 0.05,
            name,
            ha="left",
            va="bottom",
            rotation=45,
            color=colors[i],
            fontsize=9,
        )

ax = plt.gca()
for spine in ax.spines.values():
    spine.set_visible(False)
ax.spines["left"].set_visible(True)
ax.spines["left"].set_position(("outward", 50))
plt.tight_layout()
plt.show()

# Prepare team attributes
team_attr["date"] = pd.to_datetime(team_attr["date"], errors="coerce")
selected_attrs = [
    "buildUpPlaySpeed",
    "buildUpPlayDribbling",
    "defencePressure",
    "defenceAggression",
    "chanceCreationPassing",
]

latest_attrs = (
    team_attr.sort_values("date").groupby("team_api_id").last().reset_index()
)
merged_attrs = df_final.merge(
    latest_attrs[["team_api_id"] + selected_attrs],
    left_on="opponent_team_api_id",
    right_on="team_api_id",
    how="left",
)

merged_attrs["color"] = [
    (
        "green"
        if i < TOP_N
        else "red" if i >= len(merged_attrs) - TOP_N else "black"
    )
    for i in range(len(merged_attrs))
]

# Add our team attributes
our_attrs = latest_attrs[latest_attrs.team_api_id == TEAM_ID].iloc[0].to_dict()
our_attrs.update(
    {
        "team_api_id": TEAM_ID,
        "team_long_name": our_team,
        "opponent_team_api_id": TEAM_ID,
        "team_long_name_opponent": our_team,
        "color": "blue",
    }
)
merged_attrs = pd.concat(
    [merged_attrs, pd.DataFrame([our_attrs])], ignore_index=True
)


# Plot violin + swarm for attributes
palette = {
    "green": "limegreen",
    "red": "crimson",
    "black": "black",
    "blue": "cyan",
}
fig, axes = plt.subplots(
    1, len(selected_attrs), figsize=(5 * len(selected_attrs), 6), sharey=True
)

for ax, attr in zip(axes, selected_attrs):
    sns.violinplot(y=merged_attrs[attr], color="lightgray", inner=None, ax=ax)
    sns.swarmplot(
        y=merged_attrs[attr],
        hue=merged_attrs["color"],
        palette=palette,
        dodge=False,
        size=4,
        legend=False,
        ax=ax,
    )
    ax.set_title(attr)
    ax.set_xlabel("")
    ax.set_ylabel(attr if ax == axes[0] else "")

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
