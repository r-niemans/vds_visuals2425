import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# ----------------------------
# 1. Load player and attribute data
# ----------------------------
player_attributes = pd.read_csv('data/Player_Attributes.csv')
players = pd.read_csv('data/Player.csv')

# ----------------------------
# 2. Convert dates and calculate precise float age in years
# ----------------------------
players['birthday'] = pd.to_datetime(players['birthday'])
player_attributes['date'] = pd.to_datetime(player_attributes['date'])
merged = pd.merge(player_attributes, players, on='player_api_id')
merged['age'] = ((merged['date'] - merged['birthday']).dt.total_seconds() / (365.25 * 24 * 60 * 60)).round(2)

# ----------------------------
# 3. Keep latest record per player and filter for age < 24
# ----------------------------
latest = merged.sort_values('date').groupby('player_api_id').tail(1)
young = latest[latest['age'] < 24].copy()

# ----------------------------
# 4. Normalize potential and map to green→red color gradient
# ----------------------------
min_pot = young['potential'].min()
max_pot = young['potential'].max()
young['pot_norm'] = (young['potential'] - min_pot) / (max_pot - min_pot)
colormap = plt.colormaps.get_cmap('RdYlGn')
young['color'] = young['pot_norm'].apply(lambda x: f'rgba{colormap(x, bytes=True)}')

# ----------------------------
# 5. Filter players inside triangle (age ≤ 23 and above line)
# ----------------------------
# Define line from (16.5, 75) to (23, 95)
slope = (95 - 75) / (23 - 16.5)
intercept = 75 - slope * 16.5
young['triangle_line'] = slope * young['age'] + intercept

# Filter players strictly inside triangle
promising_players = young[
    (young['age'] <= 23) &
    (young['potential'] >= 75) &
    (young['potential'] <= 95) &
    (young['potential'] >= young['triangle_line'])
].copy()

# Score by potential-to-age ratio and sort
promising_players['potential_age_ratio'] = promising_players['potential'] / promising_players['age']
promising_sorted = promising_players.sort_values(by='potential_age_ratio', ascending=False)

# ----------------------------
# 6. Fit regression line
# ----------------------------
regression_data = young.dropna(subset=['age', 'potential'])
X = regression_data['age'].values.reshape(-1, 1)
y = regression_data['potential'].values
reg = LinearRegression().fit(X, y)
x_range = np.linspace(X.min(), X.max(), 100)
y_pred = reg.predict(x_range.reshape(-1, 1))

# ----------------------------
# 7. Plot with Plotly
# ----------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=young['age'],
    y=young['potential'],
    mode='markers',
    marker=dict(color=young['color'], size=10, line=dict(color='black', width=1)),
    text=young['player_name'],
    hovertemplate='<b>%{text}</b><br>Age: %{x:.2f}<br>Potential: %{y}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=x_range,
    y=y_pred,
    mode='lines',
    line=dict(color='black', dash='dot'),
    name='Trend Line'
))

# Triangle brush (updated to match logic)
fig.add_shape(
    type='path',
    path='M 16.5,75 L 16.5,95 L 23,95 Z',
    fillcolor='rgba(0,128,0,0.1)',
    line=dict(color='green'),
    layer='below'
)

fig.update_layout(
    title='Promising Young Players (Age < 24, Inside Triangle ≤ 23)',
    xaxis_title='Age',
    yaxis_title='Potential Rating',
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    showlegend=False
)

fig.show()

# ----------------------------
# 8. Output filtered & sorted promising players
# ----------------------------
print("Top Promising Players Inside Triangle (Age ≤ 23, Above Line):")
print(promising_sorted[['player_name', 'age', 'potential', 'potential_age_ratio']])