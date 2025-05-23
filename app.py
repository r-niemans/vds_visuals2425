import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

def create_heatmap(df):
    disposable_cols = ['player_api_id', 'player_fifa_api_id', 'date', 'id',
                       'gk_diving', 'gk_kicking', 'gk_handling', 'gk_positioning', 'gk_reflexes']
    attribute_cols = df.select_dtypes(include='number').columns.difference(disposable_cols + ['potential_rating_ratio']).tolist()
    attribute_cols = ['potential_rating_ratio'] + attribute_cols

    pivot_df = df.pivot_table(index=None, columns='player_name', values=attribute_cols, aggfunc='mean')
    pivot_df = pivot_df.T

    fig = go.Figure(
        data=go.Heatmap(
            opacity=1.0,
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Greys',
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
        font=dict(color='white'),
        height=800,
        width=800,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
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
    html.Div([
        html.Img(src="assets/logo.png", style={
            'height': '70px',
            'marginRight': '20px',
            'marginBottom': '30px',
        }),
        html.H1("RCD Espanyol Player Insights", style={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'marginBottom': '30px',
            'display': 'inline-block',
            'verticalAlign': 'middle'
        })
    ], style={'display': 'flex', 'alignItems': 'center', 'paddingLeft': '10px'}),

    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Promising Players', value='tab-1', style={
            'fontFamily': 'Arial'
        }, selected_style={
            'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'
        }),
        dcc.Tab(label='Heatmaps by Position', value='tab-2', style={
            'fontFamily': 'Arial'
        }, selected_style={
            'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'
        }),
        dcc.Tab(label='Team Performance Analysis', value='tab-3', style={
            'fontFamily': 'Arial'
        }, selected_style={
            'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'
        })
    ]),

    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Scatter plot'),
            dcc.Graph(figure=fig_promising, style={'display': 'inline-block', 'width': '60%'}),
            html.P("add short explanation/connection the the other plots?")
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Player Attribute Heatmaps per position'),
            # Pitch background figure shown above the heatmaps
            html.Div([
                dcc.Graph(figure=create_heatmap(df), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df2), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df3), style={'display': 'inline-block', 'width': '33%'})
            ], style={
        'display': 'flex',
        'position': 'relative',
        'alignItems': 'center',
        'width': '100%',
        'height': '100vh',
        'backgroundImage': 'url("/assets/soccer_pitch.png")',
        'backgroundSize': 'cover',
        'backgroundRepeat': 'no-repeat',
        'backgroundPosition': 'center',
        'zIndex': 0,
        'color': 'white',
    }),
], style={'position': 'relative'})
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Bar and Violin plots'),
            dcc.Graph(figure=fig_bar, style={'display': 'inline-block', 'width': '70%'}),
            dcc.Graph(figure=fig_violin,style={'display': 'inline-block', 'width': '70%'}),
            html.P("add explanation still?")
        ])

if __name__ == '__main__':
    app.run(debug=True)
