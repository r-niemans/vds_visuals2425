import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
from plotly_football_pitch import (
    make_pitch_figure,
    PitchDimensions,
    SingleColourBackground,
)
from plotly_football_pitch.pitch_dimensions import PitchDimensions, PitchOrientation

def create_heatmap(df):
    disposable_cols = ['player_api_id', 'player_fifa_api_id', 'date', 'id',
                       'gk_diving', 'gk_kicking', 'gk_handling', 'gk_positioning', 'gk_reflexes']
    attribute_cols = df.select_dtypes(include='number').columns.difference(disposable_cols + ['potential_rating_ratio']).tolist()
    attribute_cols = ['potential_rating_ratio'] + attribute_cols

    pivot_df = df.pivot_table(index=None, columns='player_name', values=attribute_cols, aggfunc='mean')
    pivot_df = pivot_df.T

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Greens',
            colorbar=dict(title='Attribute Value'),
            hovertemplate='Player: %{x}<br>Attribute: %{y}<br>Value: %{z}<extra></extra>'
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
        height=800,
        width=800,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

pitch_figure = make_pitch_figure(
    dimensions=PitchDimensions(),
    marking_colour="black",
    marking_width=2,
    pitch_background=SingleColourBackground("#81B622"),  # <- this sets the green field
    figure_width_pixels=1000,
    figure_height_pixels=600,
    orientation=PitchOrientation.HORIZONTAL
)
def create_pitch_background():
    fig = go.Figure()

    fig.update_layout(
        images=[dict(
            source="https://cdn.creazilla.com/cliparts/21466/soccer-field-clipart-xl.png",
            xref="paper", yref="paper",
            x=0, y=1,
            sizex=1, sizey=1,
            xanchor="left", yanchor="top",
            sizing="stretch",
            opacity=1,
            layer="below"
        )],
        width=1200,
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

# Importing data for the figures
df = pd.read_csv('grouped_players/fw_players.csv')
df2 = pd.read_csv('grouped_players/mf_players.csv')
df3 = pd.read_csv('grouped_players/bk_players.csv')

fig_promising = pio.read_json("figures/fig_promising.json")
fig_bar = pio.read_json("figures/fig_bar.json")
fig_violin = pio.read_json("figures/fig_violin.json")

# Defining the app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "RCD Espanyol Player Insights"

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Scatter plot', value='tab-1'),
        dcc.Tab(label='Heatmap', value='tab-2'),
        dcc.Tab(label='Bar and Violin Plots', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Scatter plot'),
            dcc.Graph(figure=fig_promising),
            html.P("add short explanation/connection the the other plots?")
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Player Attribute Heatmaps per position'),
            # Pitch background figure shown above the heatmaps
            dcc.Graph(figure=pitch_figure),
            html.Div([
                dcc.Graph(figure=create_heatmap(df), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df2), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df3), style={'display': 'inline-block', 'width': '33%'})
            ], style={
                'display': 'flex',
                'backgroundRepeat': 'no-repeat',
                'backgroundPosition': 'center',
                'padding': '10px',
                'gap': '10px'
            })
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Bar and Violin plots'),
            dcc.Graph(figure=fig_bar),
            dcc.Graph(figure=fig_violin),
            html.P("add explanation still?")
        ])

if __name__ == '__main__':
    app.run(debug=True)
