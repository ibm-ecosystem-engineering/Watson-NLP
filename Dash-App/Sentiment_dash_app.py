import os
from turtle import title
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
import watson_nlp


external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Watson NLP - Sentiment Analysis'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]


navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(html.Img(src=app.get_asset_url('ibm_logo.png'), height="30px")),
                    dbc.Col(dbc.NavbarBrand("IBM Build Labs", className="me-auto")),
                    ],
                    align="center",
                    className="w-0",
                ),
                style={"textDecoration": "bold", "margin-right": "33%"},
            ),
            dbc.Row(html.H2("Watson-Core NLP"),
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
                                ),
                                dbc.NavItem(dbc.NavLink("Report an Issue", href="https://github.ibm.com/hcbt/Watson-NLP/issues/new", target="_blank")),
                                html.Span(dcc.LogoutButton(logout_url='https://w3.ibm.com/w3publisher/ibm-build-labs'), className="ml-auto")
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

sentiment_analysis_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for Sentiment Analysis"),
                dbc.Textarea(id="sentiment-input", placeholder="Text for Sentiment analysis"),
            ],
            className="mb-3",
        )

emotion_classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for Emotion Classification"),
                dbc.Textarea(id="emotion-input", placeholder="Text for Emotion analysis"),
            ],
            className="mb-3",
        )

sentiment_button = html.Div(
    [
        dbc.Button(
            "Get Sentiment", id="sentiment-button", className="me-2", n_clicks=0
        ),
    ]
)

emotion_button = html.Div(
    [
        dbc.Button(
            "Get Emotion", id="emotion-button", className="me-2", n_clicks=0
        ),
    ]
)

sentiment_output_figure = dcc.Graph(id='sentiment-output-figure')

emotion_output_figure = dcc.Graph(id='emotion-output-figure')

df_sentiment_output = pd.DataFrame(columns=['Sentence', 'Label', 'Score'])
sentiment_output_table = dash_table.DataTable(
    # data=df_sentiment_output.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_sentiment_output.columns],
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
    id='sentiment-output-table'
)

df_emotion = pd.DataFrame(columns=['class_name', 'confidence'])
emotion_output_table = dash_table.DataTable(
    # data=df_emotion.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_emotion.columns],
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
    id='emotion-output-table'
)

def get_sentiment(text):
    # load Model 
    sentiment_model = watson_nlp.load(watson_nlp.download('sentiment_document-cnn_en_stock'))
    syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    # run the syntax model
    syntax_result = syntax_model.run(text, parsers=('token', 'lemma', 'part_of_speech'))
    # run the sentiment model on the result of the syntax analysis
    sentiment_output_python = sentiment_model.run(syntax_result, sentence_sentiment=True)
    return sentiment_output_python, sentiment_output_python.to_dict()['label']


def get_emotion(text):
    # Load the Emotion workflow model for English
    emotion_model = watson_nlp.load(watson_nlp.download('ensemble_classification-wf_en_emotion-stock'))
    emotion_output_python = emotion_model.run(text)
    return emotion_output_python

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
                        html.Div(sentiment_analysis_input),
                        html.Div(sentiment_button),
                        html.Div(id='container-button-sentiment'),
                        html.Div(sentiment_output_figure),
                        html.Div(sentiment_output_table),
                        ],
                        width=6
                    ),
                    dbc.Col(
                        children=[
                        html.Div(emotion_classification_input),
                        html.Div(emotion_button),
                        # html.Div(id='container-button-emotion'),
                        html.Div(emotion_output_figure),
                        html.Div(emotion_output_table),
                        ],
                        width=6
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
])

@app.callback(
    Output('container-button-sentiment', 'children'),
    Output('sentiment-output-figure', 'figure'),
    Output('sentiment-output-table', 'data'),
    Input('sentiment-button', 'n_clicks'),
    State('sentiment-input', 'value')
)
def sentiment_analysis_callback(n_clicks, value):
    # sentiment_output_example_processed = json.dumps(sentiment_output_example)
    sentiment_output_python = get_sentiment(value)[0]
    sentence_sentiment = [(sm['score']) for sm in sentiment_output_python.to_dict()['sentiment_mentions']]

    df_sentiment = pd.DataFrame()
    df_sentiment['sentiment_score'] = sentence_sentiment
    # Adding a column with colors
    df_sentiment["color"] = np.where(df_sentiment["sentiment_score"]<0, 'red', 'green')

    # Plot for sentiment score
    fig_sentiment = go.Figure()
    fig_sentiment.add_trace(
        go.Bar(
            name='Sentence Sentiment Score',
            y=df_sentiment['sentiment_score'],
            marker_color=df_sentiment['color'],
            # hovertext=df_sentiment['Text']
            ))
    fig_sentiment.update_layout(template=plotly_template,barmode='stack',title_text='Sentence Sentiment Score', title_x=0.5)
    

    # sentiment_output_python = json.loads(sentiment_output_example)
    sentence_sentiment = [(sm['span']['text'], sm['label'], sm['score']) for sm in sentiment_output_python.to_dict()['sentiment_mentions']]
    sentence_list = []
    label_list = []
    score_list = []
    for sent_outputs in sentence_sentiment:
        sentence_list.append(sent_outputs[0])
        label_list.append(sent_outputs[1])
        score_list.append(sent_outputs[2])
    df_sentiment_output['Sentence'] = sentence_list
    df_sentiment_output['Label'] = label_list
    df_sentiment_output['Score'] = score_list

    return get_sentiment(value)[1], fig_sentiment, df_sentiment_output.to_dict('records')

@app.callback(
    # Output('container-button-emotion', 'children'),
    Output('emotion-output-figure', 'figure'),
    Output('emotion-output-table', 'data'),
    Input('emotion-button', 'n_clicks'),
    State('emotion-input', 'value')
)
def update_output(n_clicks, value):
    # emotion_output_python = json.loads(emotion_output_example)
    emotion_output_python = get_emotion(value)
    class_name_list = []
    confidence_list = []
    for classes in emotion_output_python.to_dict()['classes']:
        class_name_list.append(classes['class_name'])
        confidence_list.append(classes['confidence'])
    df_emotion['class_name'] = class_name_list
    df_emotion['confidence'] = confidence_list

    fig_emotion = px.bar(df_emotion, x='class_name', y='confidence')
    fig_emotion.update_layout(template=plotly_template,barmode='stack',title_text='Emotion Score', title_x=0.5)
    return fig_emotion, df_emotion.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)