import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. Load player and attribute data
player_attributes = pd.read_csv('data/Player_Attributes.csv')
players = pd.read_csv('data/Player.csv')

# 2. Convert dates and calculate float age as of 2017-01-01
reference_date = pd.to_datetime('2017-01-01')
players['birthday'] = pd.to_datetime(players['birthday'])
player_attributes['date'] = pd.to_datetime(player_attributes['date'])
merged = pd.merge(player_attributes, players, on='player_api_id')
merged['age'] = ((reference_date - merged['birthday']).dt.total_seconds() / (365.25 * 24 * 60 * 60)).round(2)

# 3. Keep latest record per player and filter for age < 24
latest = merged.sort_values('date').groupby('player_api_id').tail(1)
young = latest[latest['age'] < 24].copy()

# 4. Normalize potential and color map
min_pot = young['potential'].min()
max_pot = young['potential'].max()
young['pot_norm'] = (young['potential'] - min_pot) / (max_pot - min_pot)
colormap = plt.colormaps.get_cmap('RdYlGn')
young['color'] = young['pot_norm'].apply(lambda x: f'rgba{colormap(x, bytes=True)}')

# 5. Regression line to derive opposing slope
regression_data = young.dropna(subset=['age', 'potential'])
X = regression_data['age'].values.reshape(-1, 1)
y = regression_data['potential'].values
reg = LinearRegression().fit(X, y)

# Define dynamic polygon for brush
start_x = 16.5
start_y = 75
end_x = 23.95
opposite_slope = -3 * reg.coef_[0]  # adjustable multiplier
end_y = start_y + opposite_slope * (end_x - start_x)
triangle_path = f'M {start_x},{start_y} L {start_x},95 L {end_x},95 L {end_x},{end_y} Z'

# 6. Subset: players inside polygon brush (≤23.95, between boundaries)
young['top_y'] = 95
young['bottom_y'] = start_y + opposite_slope * (young['age'] - start_x)

promising_players = young[
    (young['age'] <= 23.95) &
    (young['age'] >= start_x) &
    (young['potential'] >= young['bottom_y']) &
    (young['potential'] <= 95)
].copy()

promising_players['potential_age_ratio'] = promising_players['potential'] / promising_players['age']
promising_sorted = promising_players.sort_values(by='potential_age_ratio', ascending=False)

# 7. Fit regression line for plot
x_range = np.linspace(young['age'].min(), young['age'].max(), 100)
y_pred = reg.predict(x_range.reshape(-1, 1))

# 8. Plot with Plotly
fig = go.Figure()

# All players
fig.add_trace(go.Scatter(
    x=young['age'],
    y=young['potential'],
    mode='markers',
    marker=dict(color=young['color'], size=10, line=dict(color='black', width=1)),
    text=young['player_name'],
    hovertemplate='<b>%{text}</b><br>Age: %{x:.2f}<br>Potential: %{y}<extra></extra>'
))

# Regression trend line
fig.add_trace(go.Scatter(
    x=x_range,
    y=y_pred,
    mode='lines',
    line=dict(color='black', dash='dot'),
    name='Trend Line'
))

# Green polygon brush
fig.add_shape(
    type='path',
    path=triangle_path,
    fillcolor='rgba(0,128,0,0.1)',
    line=dict(color='green'),
    layer='below'
)

# Layout
fig.update_layout(
    title='Promising Players (Age as of Jan 1, 2017)',
    xaxis_title='Age',
    yaxis_title='Potential Rating',
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    showlegend=False
)

fig.show()

# 9. Output subset
print("Top Promising Players Inside Brush (Age as of Jan 1, 2017):")
print(promising_sorted[['player_name', 'age', 'potential', 'potential_age_ratio']])