import os
from urllib import response
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table, callback_context
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

from GrpcClient import GrpcClient

external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Watson NLP - Tone Classification'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

grpcClient = GrpcClient();

navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(dbc.NavbarBrand("Build Lab", className="me-auto")),
                    ],
                    align="center",
                    className="w-0",
                ),
                style={"textDecoration": "bold", "margin-right": "33%"},
            ),
            dbc.Row(html.H2("Watson NLP"),
            className="me-auto",
            justify='center'),
            dbc.Row(
                [
                        dbc.Nav(
                            [
                                dbc.NavItem(
                                    dbc.NavLink("©"),
                                    # add an auto margin after this to push later links to end of nav
                                    className="me-auto",
                                )
                            ],
                            # make sure nav takes up the full width for auto margin to get applied
                            className="w-100",
                        ),
                ],
        className="flex-grow-1",
        )
        ],
    color="primary",
    dark=True,
    className = "ml-auto"
)

tone_classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for Tone Classification"),
                dbc.Textarea(id="tone-input", placeholder="Text for Tone Classfication"),
            ],
            className="mb-3",
        )


tone_button = html.Div(
    [
        dbc.Button(
            "Get Tone", id="tone-button", className="me-2", n_clicks=0
        ),
    ]
)
tone_output_figure = dcc.Graph(id='tone-output-figure')

df_tone = pd.DataFrame(columns=['class_name', 'confidence'])
tone_output_table = dash_table.DataTable(
    # data=df_tone.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_tone.columns],
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
    id='tone-output-table'
)


def get_tone(text):
    # Load the Tone workflow model for English
    tone_output_python = grpcClient.call_tone_model(text)
    return tone_output_python

sentiment_table_card = html.Div(
    [
        dbc.Card(
            dbc.CardBody("This is some text within a card body"),
            className="mb-3",
        ),
    ]
)

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.Div(tone_classification_input),
                        html.Div(tone_button),
                        # html.Div(id='container-button-tone'),
                        html.Div(tone_output_figure),
                        html.Div(tone_output_table),
                        ],
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
                html.Br(),
                html.Label("This App was built using Watson NLP library."),
                html.Br(),
                html.Footer(children="Please note that this content is made available by IBM Build Lab to foster Embedded AI technology adoption. \
                                The content may include systems & methods pending patent with USPTO and protected under US Patent Laws. \
                                Copyright - 2022 IBM Corporation")
])

@app.callback(
    # Output('container-button-tone', 'children'),
    Output('tone-output-figure', 'figure'),
    Output('tone-output-table', 'data'),
    Input('tone-button', 'n_clicks'),
    State('tone-input', 'value')
)
def update_output(n_clicks, value):
    # tone_output_python = json.loads(tone_output_example)
    tone_output_python = get_tone(value)
    class_name_list = []
    confidence_list = []
    emo_dict = {emo.class_name:emo.confidence for emo in tone_output_python.classes}
    for class_name, confidence in emo_dict.items():
        class_name_list.append(class_name)
        confidence_list.append(confidence)
    df_tone['class_name'] = class_name_list
    df_tone['confidence'] = confidence_list

    fig_tone = px.bar(df_tone, x='class_name', y='confidence')
    fig_tone.update_layout(template=plotly_template,barmode='stack',title_text='Tone Score', title_x=0.5)
    return fig_tone, df_tone.to_dict('records')

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8050")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)