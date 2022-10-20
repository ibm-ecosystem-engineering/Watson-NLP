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
import pathlib

plt.switch_backend('Agg') 

external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Watson NLP - Hotel Reviews Analysis'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

DATA_PATH = pathlib.Path(__file__).parent.resolve()
FILENAME_COMPLAINTS = "data/complaints_test.csv"
FILENAME_REVIEWS= "data/reviews_test.csv"
COMPLAINTS_DF = pd.read_csv(DATA_PATH.joinpath(FILENAME_COMPLAINTS), header=0)
REVIEWS_DF = pd.read_csv(DATA_PATH.joinpath(FILENAME_REVIEWS), header=0)
# print(COMPLAINTS_DF.head())

complaints_df = COMPLAINTS_DF.iloc[:, 0]
reviews_df = REVIEWS_DF.iloc[:, 0]


# load saved Model 
reviews_svm_model = watson_nlp.load('models/svm_model_hotel_reviews_classification')
# reviews_ensemble_model = watson_nlp.load('ensemble_model_hotel_reviews_classification')
complaints_svm_model = watson_nlp.load('models/svm_model_complaints_classification')
# complaints_ensemble_model = watson_nlp.load('ensemble_model_complaints_classification')

navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(html.Img(src=app.get_asset_url('ibm_logo.png'), height="60px")),
                    dbc.Col(dbc.NavbarBrand("Build Lab", className="ml-auto"), align='center'),
                    #dbc.Col(html.H2("Watson NLP"), className="me-auto", justify='center')
                    ],
                    className="w-0",
                ),
                style={"textDecoration": "bold", "margin-right": "20%"},
            ),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            html.H2("Watson NLP", style={'textAlign': 'center'}),
                            
                        ],
                        className="me-auto",
                        align='center',
                        justify='center',
                    ),
                    dbc.Row(html.H4("Text Classification", style={'textAlign': 'center'}),
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

review_classification_sample_text = " My room was dirty and I was afraid to walk barefoot on the floor which looked as if it was not cleaned in weeks\n White furniture which looked nice in pictures was dirty too and the door looked like it was attacked by an angry dog\n My shower drain was clogged and the staff did not respond to my request to clean it\n On a day with heavy rainfall a pretty common occurrence in Amsterdam the roof in my room was leaking luckily not on the bed you could also see signs of earlier water damage\n I also saw insects running on the floor\n Overall the second floor of the property looked dirty and badly kept\n On top of all of this a repairman who came to fix something in a room next door at midnight was very noisy as were many of the guests I understand the challenges of running a hotel in an old building but this negligence is inconsistent with prices demanded by the hotel On the last night after I complained about water damage the night shift manager offered to move me to a different room but that offer came pretty late around midnight when I was already in bed and ready to sleep"
review_prefilled_input = dcc.Textarea(
        id='reviews-classification-input',
        value=review_classification_sample_text,
        style={'width': '100%', 'height': 200},
    )
review_classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Try typing your own review or use the button Fetch another review"),
                review_prefilled_input,
                # dbc.Textarea(id="reviews-classification-input", placeholder="Text for Review classification"),
            ],
            className="mb-3",
        )

review_classification_button = html.Div(
    [
        dbc.Button(
            "Classify Hotel Reviews", id="reviews-classification-button", className="me-2", n_clicks=0
        ),
    ]
)
fetch_review_button = html.Div(
    [
        dbc.Button(
            "Fetch another review", id="fetch-review-button", className="me-1", n_clicks=0
        ),
    ]
)
review_buttons = html.Div(
    [
        review_classification_button,
        fetch_review_button,
    ],
    className="d-grid gap-2 d-md-flex justify-content-md-start",
)

complaint_classification_sample_text = "Bank of America did not make the County property tax payment for XXXX and XXXX.\n I received a delinquency notice in XX/XX/XXXX and again in XX/XX/XXXX ( {$670.00} - {$35.00} late fee included ) regarding nonpayment.\n I contacted Bank of America on each occasion and was informed that it was an error on their end.\n I contacted customer service on XX/XX/XXXX to inform them of nonpayment from my escrow account.\n I was informed that this would be escalated and paid immediately.\n I checked my online account on XX/XX/XXXX to see if the payment had been made.\n The payment had not been submitted and I contacted customer once again.\n I was informed that the payment had not been paid and a manager would call me back."
# complaint_classification_sample_input = dcc.Textarea(
#         id='textarea-1',
#         value=complaint_classification_sample_text,
#         style={'width': '100%', 'height': 200},
#     )
# review_classification_sample_input = dcc.Textarea(
#         id='textarea-2',
#         value=review_classification_sample_text,
#         style={'width': '100%', 'height': 200},
#     )

complaint_prefilled_input = dcc.Textarea(
        id='complaints-classification-input',
        value=complaint_classification_sample_text,
        style={'width': '100%', 'height': 200},
    )

complaint_classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Try typing your own complaint or use the button Fetch another complaint"),
                complaint_prefilled_input,
                # dbc.Textarea(id="complaints-classification-input", placeholder="Text for Consumer complaint classification"),
            ],
            className="mb-3",
        )

complaint_classification_button = html.Div(
    [
        dbc.Button(
            "Classify consumer complaints", id="complaints-classification-button", className="me-1", n_clicks=0
        ),
    ]
)

fetch_complaint_button = html.Div(
    [
        dbc.Button(
            "Fetch another complaint", id="fetch-complaint-button", className="me-1", n_clicks=0
        ),
    ]
)

complaints_buttons = html.Div(
    [
        complaint_classification_button,
        fetch_complaint_button,
    ],
    className="d-grid gap-2 d-md-flex justify-content-md-start",
)

reviews_classification_output_figure = dcc.Graph(id='reviews-classification-output-figure')
complaints_classification_output_figure = dcc.Graph(id='complaints-classification-output-figure')

# Total complaint classification
complaints_predicted_df = pd.read_csv('data/complaints_test_predicted.csv')
complaints_predicted_df['labels'] = complaints_predicted_df.labels.str.replace("'", '')
complaints_predicted_df['labels'] = complaints_predicted_df.labels.str.strip('[]')
complaints_predicted_df['labels'] = complaints_predicted_df.labels.str.replace("Credit reporting, credit repair services, or other personal consumer reports", 'Credit reporting')
complaints_predicted_df['predicted'] = complaints_predicted_df.predicted.str.replace("Credit reporting, credit repair services, or other personal consumer reports", 'Credit reporting')

complaints_total_figure = go.Figure()
complaints_total_figure.add_trace(go.Bar(
    x=complaints_predicted_df['predicted'].value_counts().index,
    y=complaints_predicted_df['predicted'].value_counts().values,
    name='Predicted',
    # marker_color='indianred'
))
complaints_total_figure.add_trace(go.Bar(
    x=complaints_predicted_df['labels'].value_counts().index,
    y=complaints_predicted_df['labels'].value_counts().values,
    name='Actual',
    # marker_color='lightsalmon'
))
# Here we modify the tickangle of the xaxis, resulting in rotated labels.
complaints_total_figure.update_layout(barmode='group', xaxis_tickangle=-45)
complaints_total_figure.update_layout(template=plotly_template,title_text='Classification result on the test dataset for  Consumer complaints', title_x=0.5)
complaints_classification_total_figure = dcc.Graph(figure=complaints_total_figure, id='complaints-classification-total-figure')

# Total reviews classification
reviews_predicted_df = pd.read_csv('data/reviews_test_predicted.csv')
reviews_predicted_df['labels'] = reviews_predicted_df.labels.str.replace("'", '')
reviews_predicted_df['labels'] = reviews_predicted_df.labels.str.strip('[]')

reviews_total_figure = go.Figure()
reviews_total_figure.add_trace(go.Bar(
    x=reviews_predicted_df['predicted'].value_counts().index,
    y=reviews_predicted_df['predicted'].value_counts().values,
    name='Predicted',
    # marker_color='indianred'
))
reviews_total_figure.add_trace(go.Bar(
    x=reviews_predicted_df['labels'].value_counts().index,
    y=reviews_predicted_df['labels'].value_counts().values,
    name='Actual',
    # marker_color='lightsalmon'
))
# Here we modify the tickangle of the xaxis, resulting in rotated labels.
reviews_total_figure.update_layout(barmode='group', xaxis_tickangle=-45)
reviews_total_figure.update_layout(template=plotly_template,title_text='Classification result on the test dataset for Hotel Reviews', title_x=0.5)
# complaints_classification_total_figure = dcc.Graph(figure=complaints_total_figure, id='complaints-classification-total-figure')
reviews_classification_total_figure = dcc.Graph(figure=reviews_total_figure, id='reviews-classification-total-figure')

# Complaint Card components
cards_complaints = [
    dbc.Card(
        [
            html.H2(f"{83:.2f}%", className="card-title"),
            html.P("Model Test Accuracy", className="card-text"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(f"{80} / {20}", className="card-title"),
            html.P("Train / Test Split", className="card-text"),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
]

complaints_output = [
    dbc.Card(
        [
            html.H2(id='complaints-output-class', className="card-title"),
            html.P("Consumer Complaint Classification Output", className="card-text"),
        ],
        
        body=True,
        color="success",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(id='complaints-output-confidence', className="card-title"),
            html.P("Confidence Score", className="card-text"),
        ],
        body=True,
        color="warning",
        inverse=True,
    ),
]

# REviews Card components
cards_reviews = [
    dbc.Card(
        [
            html.H2(f"{94:.2f}%", className="card-title"),
            html.P("Model Test Accuracy", className="card-text"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(f"{80} / {20}", className="card-title"),
            html.P("Train / Test Split", className="card-text"),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
]
reviews_output = [
    dbc.Card(
        [
            html.H2(id='reviews-output-class', className="card-title"),
            html.P("Hotel Reviews Classification Output", className="card-text"),
        ],
        
        body=True,
        color="success",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(id='reviews-output-confidence', className="card-title"),
            html.P("Confidence Score", className="card-text"),
        ],
        body=True,
        color="warning",
        inverse=True,
    ),
]

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.H2("Consumer complaints classification"),
                        dbc.Row([dbc.Col(card) for card in cards_complaints]),
                        html.Div(complaints_classification_total_figure),
                        html.Div(complaint_classification_input),
                        complaints_buttons,
                        # html.Div(complaint_classification_button),
                        # html.Div(fetch_complaint_button),
                        # html.Div(id='container-button-classification'),
                        dbc.Row([dbc.Col(card) for card in complaints_output]),
                        html.Div(complaints_classification_output_figure),
                        # html.Div(complaint_classification_sample_input),
                        ],
                        width=6
                    ),
                    dbc.Col(
                        children=[
                        html.H2("Hotel Reviews classification"),
                        dbc.Row([dbc.Col(card) for card in cards_reviews]),
                        html.Div(reviews_classification_total_figure),
                        html.Div(review_classification_input),
                        review_buttons,
                        # html.Div(review_classification_input),
                        # html.Div(review_classification_button),
                        # html.Div(id='container-button-classification'),
                        dbc.Row([dbc.Col(card) for card in reviews_output]),
                        html.Div(reviews_classification_output_figure),
                        # html.Div(review_classification_sample_input),
                        ],
                        width=6
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

empty_output = {
  "classes": [
    {
      "class_name": "NONE/EMPTY",
      "confidence": 0
    },
    {
      "class_name": "NONE/EMPTY",
      "confidence": 0
    }
  ],
}

def classify_reviews(text: str):
    syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    use_model = watson_nlp.load(watson_nlp.download('embedding_use_en_stock'))
    if text is None:
        return empty_output
    else:     
        syntax_result = syntax_model.run(text)
        # run SVM model on top of syntax result
        svm_preds = reviews_svm_model.run(use_model.run(syntax_result, doc_embed_style='raw_text'))
        predicted_svm = svm_preds.to_dict()
        return predicted_svm

    # ensemble_preds = reviews_svm_model.run(text)
    # # predicted_ensemble = ensemble_preds.to_dict()["classes"][0]["class_name"]
    # predicted_ensemble = ensemble_preds.to_dict()
    # return predicted_ensemble

syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
use_model = watson_nlp.load(watson_nlp.download('embedding_use_en_stock'))

def classify_complaints(text: str):
    # syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    # use_model = watson_nlp.load(watson_nlp.download('embedding_use_en_stock'))
    if text is None:
        return empty_output
    else:        
        syntax_result = syntax_model.run(text)
        # run SVM model on top of syntax result
        svm_preds = complaints_svm_model.run(use_model.run(syntax_result, doc_embed_style='raw_text'))
        predicted_svm = svm_preds.to_dict()
        return predicted_svm

# predicted = []
# REVIEWS_DF['predicted'] = ''
# for i, row in REVIEWS_DF.iterrows():
#     syntax_result = syntax_model.run(str(row['reviews_narrative']))
#     svm_preds = reviews_svm_model.run(use_model.run(syntax_result, doc_embed_style='raw_text'))
#     print('svm_preds', svm_preds)
#     predicted_svm = svm_preds.to_dict()
#     print('predicted_svm', predicted_svm)
#     # print("class prediction", predicted_svm['classes'][0]['class_name'])
#     predicted.append(predicted_svm['classes'][0]['class_name'])
#     # break
# REVIEWS_DF['predicted'] = predicted
# # COMPLAINTS_DF.to_csv('complaints_test_predicted.csv')
# # print(COMPLAINTS_DF.head())
# # COMPLAINTS_DF_NEW = pd.read_csv('complaints_test_predicted.csv')
# # COMPLAINTS_DF = COMPLAINTS_DF.explode('labels')
# REVIEWS_DF.to_csv('reviews_test_predicted.csv')

@app.callback(
    Output('reviews-classification-output-figure', 'figure'),
    Output('reviews-output-class', 'children'),
    Output('reviews-output-confidence', 'children'),
    # Input('reviews-classification-button', 'n_clicks'),
    Input('reviews-classification-input', 'value')
)
def reviews_classification_callback(value):
    # sentiment_output_example_processed = json.dumps(sentiment_output_example)
    classification_output_python = classify_reviews(value)
    # print("OUTPUT CLASSES: ", classification_output_python['classes'])

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
    fig_classification.update_layout(template=plotly_template,barmode='stack',title_text='Hotel Review Classification Result', title_x=0.5)
    return fig_classification, df_classification['class_name'].iloc[0], (f"{df_classification['confidence'].iloc[0]*100:.2f}%")

@app.callback(
    Output('complaints-classification-output-figure', 'figure'),
    Output('complaints-output-class', 'children'),
    Output('complaints-output-confidence', 'children'),
    # Input('fetch-complaint-button', 'n_clicks'),
    Input('complaints-classification-input', 'value')
)
def complaints_classification_callback(value):
    classification_output_python = classify_complaints(value)
    # print("OUTPUT CLASSES: ", classification_output_python['classes'])

    df_classification = pd.DataFrame(classification_output_python['classes'])
    df_classification['class_name'] = df_classification.class_name.str.replace("Credit reporting, credit repair services, or other personal consumer reports",
                                                                         'Credit reporting')
    # Adding a column with colors
    # df_classification["color"] = np.where(df_classification["class_name"]=='Complaint', 'red', 'green')

    # Plot for sentiment score
    fig_classification = go.Figure()
    fig_classification.add_trace(
        go.Bar(
            name='Consumer complaint category',
            y=df_classification['confidence'],
            x=df_classification['class_name'],
            # marker_color=df_classification['color'],
            # hovertext=df_classification['Text']
            ))
    fig_classification.update_layout(template=plotly_template,barmode='stack',title_text='Consumer complaints Classification Result', title_x=0.5)
    return fig_classification, df_classification['class_name'].iloc[0], (f"{df_classification['confidence'].iloc[0]*100:.2f}%")

@app.callback(
    Output('complaints-classification-input', 'value'),
    Input('fetch-complaint-button', 'n_clicks'),
)
def fetch_complaint_from_dataset(n_clicks):
    # print("n_clicks", complaints_df.values[n_clicks])
    return complaints_df.values[n_clicks]

@app.callback(
    Output('reviews-classification-input', 'value'),
    Input('fetch-review-button', 'n_clicks'),
)
def fetch_complaint_from_dataset(n_clicks):
    # print("n_clicks", reviews_df.values[n_clicks])
    return reviews_df.values[n_clicks]

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8051, debug=True)
