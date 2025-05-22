import pandas as pd
import numpy as np
import plotly.graph_objects as go

TEAM_ID = 8558
BASELINE = 1.1
TOP_N = 5

# Load data
data_path = "data/"
matches = pd.read_csv(data_path + "Match.csv")
match_possession = pd.read_csv(data_path + "Match_Possesion.csv")
match_shots_on = pd.read_csv(data_path + "Match_Shots_On.csv")
match_shots_off = pd.read_csv(data_path + "Match_Shots_Off.csv")
team = pd.read_csv(data_path + "Team.csv")
team_attr = pd.read_csv(data_path + "Team_Attributes.csv")


# Points calculation function
def pts(f, a):
    return 3 if f > a else 1 if f == a else 0


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

# Team Names
our_team = team.loc[team.team_api_id == TEAM_ID, "team_long_name"].values[0]
avg_pts = avg_pts.merge(
    team[["team_api_id", "team_long_name"]],
    left_on="opponent_team_api_id",
    right_on="team_api_id",
)
df_final = avg_pts.sort_values("points", ascending=False).reset_index(
    drop=True
)

# Classification colors
colors = [
    (
        "limegreen"
        if i < TOP_N
        else "crimson" if i >= len(df_final) - TOP_N else "grey"
    )
    for i in range(len(df_final))
]
df_final["classification"] = [
    (
        "Top 5"
        if i < TOP_N
        else "Bottom 5" if i >= len(df_final) - TOP_N else "Others"
    )
    for i in range(len(df_final))
]
color_map = {
    "Top 5": "limegreen",
    "Bottom 5": "crimson",
    "Others": "grey",
    "Our Team": "cyan",
}

# ---- BAR CHART ----
fig_bar = go.Figure()
for idx, row in df_final.iterrows():
    height = abs(row.points - BASELINE)
    bottom = BASELINE if row.points >= BASELINE else row.points
    fig_bar.add_trace(
        go.Bar(
            x=[row.team_long_name],
            y=[height],
            base=[bottom],
            marker_color=colors[idx],
            name=row.classification,
            hoverinfo="text",
            hovertext=f"{row.team_long_name}: {row.points:.2f} points",
        )
    )

fig_bar.update_layout(
    title=f"{our_team}: Average Points Earned Against Opponents (2008–2016)",
    xaxis_title="Opponent Team",
    yaxis_title="Average Points",
    showlegend=False,
    plot_bgcolor="white",  # <--- This makes plot area white
    paper_bgcolor="white",  # <--- This makes surrounding canvas white
)

# Draw baseline
fig_bar.add_shape(
    type="line",
    x0=-0.5,
    y0=BASELINE,
    x1=len(df_final) - 0.5,
    y1=BASELINE,
    line=dict(color="black", dash="dash"),
)

fig_bar.show()

# ---- VIOLIN PLOTS ----

# Team Attributes (latest)
team_attr["date"] = pd.to_datetime(team_attr["date"], errors="coerce")
latest_attrs = (
    team_attr.sort_values("date").groupby("team_api_id").last().reset_index()
)
selected_attrs = [
    "buildUpPlaySpeed",
    "buildUpPlayDribbling",
    "defencePressure",
    "defenceAggression",
    "chanceCreationPassing",
]
our_team = pd.DataFrame(
    {
        "opponent_team_api_id": [8558],
        "points": [0],
        "team_api_id": [8558],
        "team_long_name": "RCD Espanyol",
        "classification": "Our Team",
    }
)
df_final = pd.concat([df_final, our_team], ignore_index=True)

merged_attrs = df_final.merge(
    latest_attrs[["team_api_id"] + selected_attrs],
    left_on="opponent_team_api_id",
    right_on="team_api_id",
)

# Possession and Shots (averages per match)
match_possession_avg = (
    match_possession.groupby("match_id")[["homepos", "awaypos"]]
    .mean()
    .reset_index()
)
match_team_mapping = matches.merge(
    match_possession_avg, left_on="id", right_on="match_id"
)

home_pos = match_team_mapping[["home_team_api_id", "homepos"]].rename(
    columns={"home_team_api_id": "team_api_id", "homepos": "possession"}
)
away_pos = match_team_mapping[["away_team_api_id", "awaypos"]].rename(
    columns={"away_team_api_id": "team_api_id", "awaypos": "possession"}
)
possession_long = pd.concat([home_pos, away_pos])

shots_on = (
    match_shots_on.groupby(["match_id", "team"])
    .size()
    .groupby("team")
    .mean()
    .reset_index(name="shots_on")
)
shots_off = (
    match_shots_off.groupby(["match_id", "team"])
    .size()
    .groupby("team")
    .mean()
    .reset_index(name="shots_off")
)

team_metrics = (
    possession_long.groupby("team_api_id")["possession"].mean().reset_index()
)
team_metrics = team_metrics.merge(
    shots_on, left_on="team_api_id", right_on="team", how="left"
).merge(shots_off, left_on="team_api_id", right_on="team", how="left")

merged_attrs = merged_attrs.merge(
    team_metrics, left_on="opponent_team_api_id", right_on="team_api_id"
)
merged_attrs["classification"] = df_final["classification"]

for attr in selected_attrs + ["possession", "shots_on", "shots_off"]:
    merged_attrs["attr_name"] = attr

    fig = go.Figure()
    fig.add_trace(
        go.Violin(
            y=merged_attrs[attr],
            x=[attr] * len(merged_attrs),
            name=attr,
            box_visible=False,
            meanline_visible=True,
            fillcolor="rgba(255,255,255,0.7)",
            line_color="black",
            showlegend=False,
        )
    )

    # Overlay colored scatter dots for each classification
    for class_label in ["Top 5", "Bottom 5", "Others", "Our Team"]:
        sub = merged_attrs[merged_attrs["classification"] == class_label]
        fig.add_trace(
            go.Scatter(
                x=[attr] * len(sub),
                y=sub[attr],
                mode="markers",
                marker=dict(
                    color=color_map[class_label],
                    size=10,
                    line=dict(width=1, color="black"),
                ),
                name=class_label,
                text=sub["team_long_name"],
                hovertemplate="%{text}<br>" + attr + ": %{y:.2f}",
                showlegend=True if attr == selected_attrs[0] else False,
            )
        )

    fig.update_layout(
        plot_bgcolor="white",  # Inside the axes
        paper_bgcolor="white",  # Outside the axes
        title=f"{our_team}: Distribution of {attr} (2008–2016)",
        yaxis_title=attr,
        xaxis=dict(showticklabels=False),
        legend=dict(title="Classification"),
    )
    fig.show()
