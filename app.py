import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
from heatmap import create_heatmap

# Import data for heatmaps
df_fw = pd.read_csv('grouped_players/fw_players.csv')
df_mf = pd.read_csv('grouped_players/mf_players.csv')
df_bk = pd.read_csv('grouped_players/bk_players.csv')

fig_promising = pio.read_json("figures/fig_promising.json")
fig_bar = pio.read_json("figures/fig_bar.json")
fig_violin = pio.read_json("figures/fig_violin.json")

# Define the app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "RCD Espanyol Player Insights"
app.layout = html.Div([
    html.Div([
        html.Img(src="assets/logo.png", style={
            'height': '70px',
            'marginRight': '20px',
            'marginBottom': '30px',
        }),
        html.H1("Player Insights for RCD Espanyol", style={
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
            dcc.Graph(figure=fig_promising, style={'display': 'inline-block', 'width': '60%'})
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Player Attribute Heatmaps per position'),
            html.Div([
                dcc.Graph(figure=create_heatmap(df_bk, 'bk'), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df_mf, 'mf'), style={'display': 'inline-block', 'width': '33%'}),
                dcc.Graph(figure=create_heatmap(df_fw, 'fw'), style={'display': 'inline-block', 'width': '33%'})
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
            dcc.Graph(figure=fig_violin,style={'display': 'inline-block', 'width': '70%'})
        ])

if __name__ == '__main__':
    app.run(debug=True)
