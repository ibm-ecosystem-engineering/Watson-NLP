import os
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
from wordcloud import WordCloud
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import watson_nlp
import io
import base64

plt.switch_backend('Agg') 

external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Watson NLP - Hotel Reviews Analysis'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

# load saved Model 
svm_model = watson_nlp.load('svm_model_hotel_reviews_classification')
# ensemble_model = watson_nlp.load('ensemble_model_hotel_reviews_classification')

navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(html.Img(src=app.get_asset_url('ibm_logo.png'), height="40px")),
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
                                ),
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

classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for Classification"),
                dbc.Textarea(id="classification-input", placeholder="Text for Review classification"),
            ],
            className="mb-3",
        )

classification_button = html.Div(
    [
        dbc.Button(
            "Classify Hotel Reviews", id="classification-button", className="me-2", n_clicks=0
        ),
    ]
)

topic_button = html.Div(
    [
        dbc.Button(
            "Get Topics by company", id="topics-button", className="me-2", n_clicks=0
        ),
    ]
)

keywords_button = html.Div(
    [
        dbc.Button(
            "Get Keywords", id="keywords-button", className="me-2", n_clicks=0
        ),
    ]
)

topic_output_figure = dcc.Graph(id='topic-output-figure')
keywords_output_figure = html.Img(id='keywords-output-figure')
phrases_output_figure = html.Img(id='phrases-output-figure')
classification_output_figure = dcc.Graph(id='classification-output-figure')

# Extracting all Topic names , Keywords , Phrases & Sentences from the Topic Model
def extract_topics_information(topic_model_output):
    topic_dict=[]
    for topic in topic_model_output['clusters']:
        topic_val = {'Topic Name':topic['topicName'],'Total Documents':topic['numDocuments'],'Percentage':topic['percentage'],'Cohesiveness':topic['cohesiveness'],'Keywords':topic['modelWords'],'Phrases':topic['modelNgram'],'Sentences':topic['sentences']}
        topic_dict.append(topic_val)
    return topic_dict

# Most Important top N keywoprds & Phrases 
# See Top -5 Topics Keywords & Phrases 
def create_keywords_dict(keywords):
    keywords_list =[]
    for keys in keywords:
        dic ={}
        for key in keys:
            key_value = key.split(',')
            dic[key_value[0].split('(')[0]] = float(key_value[1])
        keywords_list.append(dic)
    return keywords_list

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.Div(classification_input),
                        html.Div(classification_button),
                        # html.Div(id='container-button-classification'),
                        html.Div(classification_output_figure),
                        ],
                        width=6
                    ),
                    # dbc.Col(
                    #     children=[
                    #     html.Div(emotion_classification_input),
                    #     html.Div(emotion_button),
                    #     # html.Div(id='container-button-emotion'),
                    #     html.Div(emotion_output_figure),
                    #     html.Div(emotion_output_table),
                    #     ],
                    #     width=6
                    # ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
])

def classify_reviews(text):
    syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    use_model = watson_nlp.load(watson_nlp.download('embedding_use_en_stock'))
    syntax_result = syntax_model.run(text)
    # run SVM model on top of syntax result
    svm_preds = svm_model.run(use_model.run(syntax_result, doc_embed_style='raw_text'))
    predicted_svm = svm_preds.to_dict()

    # ensemble_preds = ensemble_model.run(text)
    # # predicted_ensemble = ensemble_preds.to_dict()["classes"][0]["class_name"]
    # predicted_ensemble = ensemble_preds.to_dict()
    # return predicted_ensemble
    return predicted_svm

@app.callback(
    # Output('container-button-classification', 'children'),
    Output('classification-output-figure', 'figure'),
    Input('classification-button', 'n_clicks'),
    State('classification-input', 'value')
)
def reviews_classification_callback(n_clicks, value):
    # sentiment_output_example_processed = json.dumps(sentiment_output_example)
    classification_output_python = classify_reviews(value)
    print("OUTPUT CLASSES: ", classification_output_python['classes'])

    df_classification = pd.DataFrame(classification_output_python['classes'])
    # Adding a column with colors
    df_classification["color"] = np.where(df_classification["class_name"]=='Complaint', 'red', 'green')

    # Plot for sentiment score
    fig_classification = go.Figure()
    fig_classification.add_trace(
        go.Bar(
            name='Hotel Review category',
            y=df_classification['confidence'],
            x=df_classification['class_name'],
            marker_color=df_classification['color'],
            # hovertext=df_classification['Text']
            ))
    fig_classification.update_layout(template=plotly_template,barmode='stack',title_text='Hotel Review Classification', title_x=0.5)
    return fig_classification

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8051, debug=True)
