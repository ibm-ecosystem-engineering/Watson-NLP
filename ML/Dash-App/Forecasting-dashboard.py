import os
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash_daq as daq
from dash import Input, Output, State, html
from dash.dependencies import Input, Output
import datetime, random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
import numpy as np
import re
import json
from dash.dependencies import Input, Output
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller,acf, pacf
from statsmodels.graphics.tsaplots import plot_predict
from statsmodels.tsa.arima.model import ARIMA
from dateutil.parser import parse
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from fbprophet import Prophet

xls = pd.ExcelFile('Agarwal Automobiles Fuel Station Sales Data.xlsx')

# Creating dataframe for each section of the excel sheet to be combined later
df_daily1 = pd.read_excel(xls, 'Exhibit 7- Daily Sales Data', header=0, usecols = "A:E")
df_daily2 = pd.read_excel(xls, 'Exhibit 7- Daily Sales Data', header=0, usecols = "F:J")
df_daily3 = pd.read_excel(xls, 'Exhibit 7- Daily Sales Data', header=0, usecols = "K:O")
df_daily4 = pd.read_excel(xls, 'Exhibit 7- Daily Sales Data', header=0, usecols = "P:T")

# Dropping rows which have year header in the excel sheet
df_daily1 = df_daily1.drop(df_daily1.index[0])
df_daily3 = df_daily3.drop(df_daily3.index[60])

df_daily2 = df_daily2.rename(columns = lambda x : str(x)[:-2])
df_daily3 = df_daily3.rename(columns = lambda x : str(x)[:-2])
df_daily4 = df_daily4.rename(columns = lambda x : str(x)[:-2])

# Dropping last 3 rows of the 4th dataframe
df_daily4.drop(df_daily4.tail(3).index,
        inplace = True)

# Joining all the 4 dataframes together
df_daily = pd.concat([df_daily1, df_daily2, df_daily3, df_daily4])
df_daily['Date'] =  pd.to_datetime(df_daily['Date'])

df_daily_diesel = df_daily[['Date', 'Dies']]
df_daily_diesel = df_daily_diesel.set_index('Date')
df_daily_diesel.plot()

plt.switch_backend('Agg') 

external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Fuel Station Forecasting and Inventory Management'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(dbc.NavbarBrand("Laxmi Kumari", className="ml-auto")),
                    ],
                    className="w-0",
                ),
                style={"textDecoration": "bold", "margin-right": "20%"},
            ),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            html.H2("Fedex Dashboard", style={'textAlign': 'center'}),
                            
                        ],
                        className="me-auto",
                        align='center',
                        justify='center',
                    ),
                    dbc.Row(html.H4("Fuel Station Forecasting and Inventory Management", style={'textAlign': 'center'}),
                        className="me-auto",
                        align='center',
                        justify='center'
                    ),
                ],
                align = 'center'
            ),
            dbc.Col([]),
        ],
    color="primary",
    dark=True,
    className = "ml-auto"
)

df_topic_output = pd.DataFrame(columns=['Topic Name', 'Sentences'])
topic_output_table = dash_table.DataTable(
    # data=df_sentiment_output.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_topic_output.columns],
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'textAlign': 'left',
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'width': 'auto',
    },
    style_cell={
        'textAlign': 'left',
        'font-family':'sans-serif',
        'headerAlign': 'left'
    },
    style_table={'overflowX': 'scroll'},
    style_as_list_view=True,
    sort_action='native',
    sort_mode='multi',
    id='topic-output-table'
)

topic_button = html.Div(
    [
        dbc.Button(
            "Get Topics by company", id="topics-button", className="me-2", n_clicks=0
        ),
        dbc.Button("Data Source URL: Consumer Complaint Database", id="data-source", color="link", className="me-1",
                     href="https://www.consumerfinance.gov/data-research/consumer-complaints/"),
    ]
)


daily_diesel_figure = dcc.Graph(figure=df_daily_diesel.plot(), id='topic-output-figure')

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        # dcc.Dropdown(["Discover Bank", "Navient Solutions, LLC.", "Synchrony Financial", "Paypal Holdings, Inc ", "Ocwen Financial Corporation"], "Discover Bank", id='bank-dropdown',style={'color':'#00361c'}),
                        # html.Div(topic_button),
                        html.Div(daily_diesel_figure),
                        ],
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
])

# @app.callback(
#     Output('topic-output-figure', 'figure'),
#     Input('topics-button', 'n_clicks'),
#     Input('bank-dropdown', 'value'),
# )
# def topic_modeling_callback(n_clicks, value):
#     return 

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8051")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)
