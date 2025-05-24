import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
from collections import defaultdict
import plotly.io as pio

players = pd.read_csv('data/Player.csv')
player_atts = pd.read_csv('data/Player_Attributes.csv')
teams = pd.read_csv('data/Team.csv')
matches = pd.read_csv('data/Match.csv')
leagues = pd.read_csv('data/League.csv')
positions = pd.read_csv('data/PositionReference.csv')

player_atts['potential_rating_ratio'] = ((player_atts['potential'] / player_atts['overall_rating']) * 100)

teams[teams['team_long_name']=='RCD Espanyol']

matches['date'] = pd.to_datetime(matches['date'])
rcde_matches = matches[matches['home_team_api_id']== 8558]

filtered_players_rcde = [col for col in rcde_matches.columns if re.match(r'home_player_\d+$', col)]

# add player name column
player_atts = player_atts.merge(players[['player_api_id', 'player_name']], on='player_api_id', how='left')

# From the scatterplot
with open("data/promising_names.txt", "r") as f:
    promising_names = [line.strip() for line in f]

# Retain the most promising players
promising_players = player_atts[player_atts['player_name'].isin(promising_names)]

player_cols = [col for col in matches.columns if re.fullmatch(r'home_player_\d+', col) or re.fullmatch(r'away_player_\d+', col)]

for col in player_cols:
    # Find the corresponding Y column
    y_col = col.replace('home_player_', 'home_player_Y')
    y_col_away = col.replace('away_player_', 'away_player_Y')

    matches[col] = matches[col].astype('Int64')

    # Merge with players table
    matches = matches.merge(
        players,
        left_on=col,
        right_on='player_api_id',
        how='left',
        suffixes=('', f'_{col}_info')
    )

    matches[f'{col}_position'] = matches[y_col]

relevant_columns = [col for col in matches.columns if (
    ("home_player" in col or "away_player" in col) and
    ("_position" in col or "player_api_id" in col or "player_name" in col)
)]

players_filtered = matches[relevant_columns]

name_cols = [col for col in players_filtered.columns if 'player_name_home_player_' in col or 'player_name_away_player_' in col]
pos_cols = [col for col in players_filtered.columns if re.fullmatch(r'home_player_\d+_position', col) or re.fullmatch(r'away_player_\d+_position', col)]

player_position_dict = {}

for name_col in name_cols:
    match = re.search(r'(home|away)_player_(\d+)', name_col)
    if not match:
        continue
    prefix, player_number = match.groups()
    pos_col = f'{prefix}_player_{player_number}_position'

    if pos_col not in players_filtered.columns:
        print(f"Warning: {pos_col} not found in columns.")
        continue

    for name, pos in zip(players_filtered[name_col], players_filtered[pos_col]):
        if pd.notna(name) and pd.notna(pos) and pos<12:
            player_position_dict[name] = int(pos)

player_position_dict

# only get the role_y information
pos_role_dict = {}
for position, role in zip(positions['player_pos_y'], positions['role_y']):
    pos_role_dict[position] = role

# map player position numbers and map to role
player_role_dict = {player: pos_role_dict.get(int(position), 'Unknown') for player, position in player_position_dict.items()}

player_role_dict

# sort player names per role on the soccer pitch
roles = defaultdict(list)
for player, role in player_role_dict.items():
    roles[role].append(player)

unique_roles = sorted(roles.keys())
role_counts = {role: len(players) for role, players in roles.items()}

gk_player_names = roles['GK']
bk_player_names = roles['BK']
mf_player_names = roles['MF']
fw_player_names = roles['FW']

# initalize dataframes to base the heatmaps on
bk_players = promising_players[promising_players['player_name'].isin(bk_player_names)]
mf_players = promising_players[promising_players['player_name'].isin(mf_player_names)]
fw_players = promising_players[promising_players['player_name'].isin(fw_player_names)]

fw_players.to_csv("fw_players.csv", index=False)
mf_players.to_csv("mf_players.csv", index=False)
bk_players.to_csv("bk_players.csv", index=False)

pio.renderers.default = "notebook_connected"

def create_heatmap(df, position):
    bk = [
        "marking", "standing_tackle", "sliding_tackle", "interceptions", "strength",
        "stamina", "aggression", "jumping", "heading_accuracy", "short_passing",
        "reactions", "vision"
    ]
    mf = [
        "short_passing", "long_passing", "ball_control", "vision", "dribbling",
        "interceptions", "stamina", "reactions", "positioning", "aggression",
        "shot_power", "curve", "free_kick_accuracy", "standing_tackle", "sliding_tackle"
    ]
    fw = [
        "finishing", "shot_power", "positioning", "dribbling", "acceleration",
        "sprint_speed", "ball_control", "volleys", "heading_accuracy", "agility",
        "reactions", "penalties", "curve"
    ]

    if position == 'bk':
        attributes = bk
    elif position == 'mf':
        attributes = mf
    elif position == 'fw':
        attributes = fw
    else:
        raise ValueError("Position incorrect")

    columns_to_keep = ['player_name', 'potential_rating_ratio'] + attributes
    df = df[columns_to_keep].dropna()
    df['potential_rating_ratio'] = df['potential_rating_ratio'].astype(int)
    df = df.sort_values(by='potential_rating_ratio', ascending=False)

    pivot_df = df.set_index('player_name')[['potential_rating_ratio'] + attributes]
    pivot_df = pivot_df.sort_values(by='potential_rating_ratio', ascending=False)

    pio.renderers.default = "notebook_connected"

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Viridis',
            colorbar=dict(title='Attribute Value'),
            hovertemplate='Player: %{y}<br>Attribute: %{x}<br>Value: %{z}<extra></extra>'
        )
    )

    fig.update_layout(
        xaxis=dict(
            title=dict(text='Attributes', font=dict(size=12)),
            tickangle=45,
            tickfont=dict(size=10)
        )
        ,
        yaxis=dict(
            title=dict(text='Player Names', font=dict(size=12)),
            tickfont=dict(size=10)
        )
        ,
        font=dict(color='white'),
        height=800,
        width=800,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


create_heatmap(fw_players, 'fw')
create_heatmap(bk_players, 'bk')
create_heatmap(mf_players, 'mf')