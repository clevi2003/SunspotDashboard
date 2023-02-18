import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import dash_daq as daq


def full_plot(df, x_col, y_col, window, filter_col, min_filter=None, max_filter=None):
    """
    :param df: pandas dataframe
        contains the relevant data
    :param x_col: string
        the name of the x column in df
    :param y_col: string
        the name of the y column in df
    :param window: integer
        the window for calculating a moving average
    :param filter_col: string
        the name of the column to filter on
    :param min_filter: integer
        minimum filter column value to keep
    :param max_filter: integer
        maximum filter column value to keep
    :return: none
    """
    # filter the df if filter conditions are input
    if min_filter is not None:
        df = df[df[filter_col] >= min_filter].reset_index()
    if max_filter is not None:
        df = df[df[filter_col] <= max_filter].reset_index()
    # plot the df as is and plot the moving average of the y column
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            name='Monthly Average'))
    df_moving_avg = moving_avg(df, y_col, window)
    fig.add_trace(
        go.Scatter(
            x=df_moving_avg[x_col],
            y=df_moving_avg["y new"],
            name='Moving Average'))
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Average Monthly Sunspots')

    return fig


def moving_avg(df, y_col, window):
    """
    :param df: pandas dataframe
        contains the relevant data
    :param y_col: string
        the name of the y column in df
    :param window: integer
        the window for a moving average
    :return: df: pandas dataframe
        contains the new column with the moving average of the y column
    """
    y_new = []
    # calculate the moving average for each row of df
    for i in range(len(df)):
        total = 0
        count = 0
        # get the total for average calculation by adding each row within window from the current row
        for j in range(window):
            if i - j > 0:
                count += 1
                total += df.at[i - j, y_col]
            if i + j < len(df) - 1:
                total += df.at[i + j, y_col]
                count += 1
        total = total / count
        # populate the moving average list and then make it a column in df
        y_new.append(total)
    df["y new"] = y_new
    return df


def smooth_plot(df, x_col, y_col, window):
    """
    :param df: pandas dataframe
        contains the relevant data
    :param x_col: string
        the name of the x column in df
    :param y_col: string
        the name of the y column in df
    :param window: integer
        the window for calculating a moving average
    :return: none
    """
    # add a moving average column to the input df and plot
    df = moving_avg(df, y_col, window)
    fig = px.line(df, x_col, "y new")
    fig.data[0].line.color = "gold"
    return fig


def plot_variability(df, cycle_length):
    """

    :param df: dataframe
        contains relevant data
    :param cycle_length: float
        mod value for cycle overlay
    :return: fig
        plotly figure
    """
    """Plots variability of sunspot cycle by overlaying cycles"""

    # Changes dates, so that cycles are overlayed
    df['Cycle Year'] = df['Fraction Date'] % cycle_length

    # plots number of sunspots by cycle year
    fig = px.scatter(
        df,
        x='Cycle Year',
        y='Sunspots',
        title='Sunspot Cycle: ' + str(cycle_length))
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Number of Sunspots')

    return fig


def main():
    df = pd.read_csv('SN_m_tot_V2.0.csv', header=None, delimiter=';')
    df = df.rename({0: 'Year', 1: 'Month', 2: 'Fraction Date', 3: 'Sunspots', 4: 'Standard Deviation',
                    5: 'Observations', 6: 'Definitive/Provisional Marker'}, axis=1)

    app = Dash(__name__)

    telescopes = {
        "EIT 171": "https://soho.nascom.nasa.gov/data/realtime/eit_171/1024/latest.jpg",
        "EIT 195": "https://soho.nascom.nasa.gov/data/realtime/eit_195/1024/latest.jpg",
        "EIT 284": "https://soho.nascom.nasa.gov/data/realtime/eit_284/1024/latest.jpg",
        "EIT 304": "https://soho.nascom.nasa.gov/data/realtime/eit_304/1024/latest.jpg",
        "SDO/HMI Continuum": "https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg",
        "SDO/HMI Magnetogram": "https://soho.nascom.nasa.gov/data/realtime/hmi_mag/1024/latest.jpg",
        "LASCO C2": "https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg",
        "LASCO C3": "https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg"}
    fig = plot_variability(df, 11)
    fig1 = full_plot(df, "Fraction Date", "Sunspots", 5, "Year", min_filter=1950)

    app.layout = html.Div(children=[
        # All elements from the top of the page
        html.Div([
            html.H1(children='Live Image of the Sun'),
            html.Img(
                id="sun_pic",
                src="https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg",
                width="400",
                height="400"
            ),
            html.P('Select Telescope Filter:'),
            dcc.Dropdown(
                id='telescope_filter',
                options=list(telescopes.keys()),
                value="EIT 171",
                clearable=False
            )

        ]),
        html.Div([
            html.H1(children='Sunspot Variability'),
            dcc.Graph(
                id='graph',
                figure=fig),
            html.P("Select cycle length"),
            dcc.Slider(
                id='cycle_length',
                min=9,
                max=13,
                step=0.1,
                value=11)
        ]),
        # New Div for all elements in the new 'row' of the page
        html.Div(children=[
            html.H1(children='Monthly Average Sunspots'),
            dcc.Graph(
                id='graph1',
                figure=fig1),
            html.P("Earliest Year to Include"),
            daq.NumericInput(
                id='min_filter',
                min=1749,
                max=1950,
                value=1950
            ),
            html.P("Latest Year to Include"),
            daq.NumericInput(
                id='max_filter',
                min=1951,
                max=2022,
                value=2020),
            html.P("Window for the Moving Average"),
            dcc.Slider(
                id='window',
                min=5,
                max=10,
                step=1,
                value=10),
        ]),
    ])

    @app.callback(
        Output("sun_pic", "src"),
        Input("telescope_filter", "value")
    )
    def update_sun_picture(telescope_filter):
        """

        :param telescope_filter: string
            the filter to of the sun live image to retrieve the link for
        :return:
            link to the desred live image of the sun
        """
        return telescopes[telescope_filter]

    @app.callback(
        Output("graph", "figure"),
        Input("cycle_length", "value")
    )
    def update_variability(cycle_length):
        """

            :param cycle_length: float
                mod value for cycle overlay
            :return: fig
                updated plotly figure
        """
        """Plots variability of sunspot cycle by overlaying cycles"""

        # Changes dates, so that cycles are overlayed
        df['Cycle Year'] = df['Fraction Date'] % cycle_length

        # plots number of sunspots by cycle year
        fig = px.scatter(
            df,
            x='Cycle Year',
            y='Sunspots',
            title='Sunspot Cycle: ' + str(cycle_length))
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Number of Sunspots')

        return fig

    @app.callback(
        Output('graph1', 'figure'),
        Input('window', 'value'),
        Input('min_filter', 'value'),
        Input('max_filter', 'value'))
    def update_fig(window=10, min_filter=1950, max_filter=2020):
        """
        :param window: integer
            the window for calculating a moving average
        :param min_filter: integer
            minimum filter column value to keep
        :param max_filter: integer
            maximum filter column value to keep
        :return: fig
            updated plotly figure
        """

        filter_col = 'Year'
        x_col = "Fraction Date"
        y_col = 'Sunspots'
        # filter the df if filter conditions are input
        df_new = df[df[filter_col] >= min_filter].reset_index()
        df_new = df_new[df_new[filter_col] <= max_filter].reset_index()
        # plot the df as is and plot the moving average of the y column
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_new[x_col],
                y=df_new[y_col],
                name='Monthly Average'))
        df_moving_avg = moving_avg(df_new, y_col, window)
        fig.add_trace(
            go.Scatter(
                x=df_moving_avg[x_col],
                y=df_moving_avg["y new"],
                name='Moving Average'))
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Average Monthly Sunspots')
        return fig

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
