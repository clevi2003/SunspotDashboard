import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Input, Output


def plot_variability(df, cycle_length):
    """Plots variability of sunspot cycle by overlaying cycles"""

    # Changes dates, so that cycles are overlayed
    df['Cycle Year'] = df['Fraction Date'] % cycle_length

    # plots number of sunspots by cycle year
    fig = px.scatter(df, x='Cycle Year', y='Sunspots', title='Sunspot Cycle: ' + str(cycle_length))
    fig.update_layout(xaxis_title='Year', yaxis_title='Number of Sunspots')

    return fig


df = pd.read_csv('SN_m_tot_V2.0.csv', header=None, delimiter=';')
df = df.rename({0: 'Year', 1: 'Month', 2: 'Fraction Date', 3: 'Sunspots', 4: 'Standard Deviation',
                5: 'Observations', 6: 'Definitive/Provisional Marker'}, axis=1)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[
            dcc.Graph(id="graph", style={'width': '100vw', 'height': '90vh'}),
            html.P("Select cycle length"),
            dcc.Slider(id='cycle_length', min=9, max=13, step=0.1, value=11)
        ]),
        dcc.Tab(label='Tab two', children=[
            dcc.Graph(id='graph', style={'width': '100vw', 'height': '90vh'}),
            html.P("Select attribute"),
            dcc.Dropdown(id='something', options=sorted(list(df.columns)),
                 value = 'Sunspots', clearable = False)
        ]),
        dcc.Tab(label='Tab three', children=[
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [2, 4, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            )
        ]),
    ])
])

@app.callback(
    Output("graph", "figure"),
    Input("cycle_length", "value")
)
def plot_variability(cycle_length):
    """Plots variability of sunspot cycle by overlaying cycles"""

    # Changes dates, so that cycles are overlayed
    df['Cycle Year'] = df['Fraction Date'] % cycle_length

    # plots number of sunspots by cycle year
    fig = px.scatter(df, x='Cycle Year', y='Sunspots', title='Sunspot Cycle: ' + str(cycle_length))
    fig.update_layout(xaxis_title='Year', yaxis_title='Number of Sunspots')

    return fig

def plot_something(something):
    fig = px.scatter(df, x='Fraction Date', y='Sunspots')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

