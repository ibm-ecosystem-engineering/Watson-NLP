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
FILENAME = "data/complaints_test.csv"
GLOBAL_DF = pd.read_csv(DATA_PATH.joinpath(FILENAME), skiprows=1, header=0)
# print(GLOBAL_DF.head())
complaints_df = GLOBAL_DF.iloc[:, 0]

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
                    dbc.Col(html.Img(src=app.get_asset_url('ibm_logo.png'), height="30px")),
                    dbc.Col(dbc.NavbarBrand("Build Lab", className="ml-auto")),
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

review_classification_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for hotel review classification"),
                dbc.Textarea(id="reviews-classification-input", placeholder="Text for Review classification"),
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

complaint_classification_sample_text = "Bank of America did not make the County property tax payment for XXXX and XXXX.\n I received a delinquency notice in XX/XX/XXXX and again in XX/XX/XXXX ( {$670.00} - {$35.00} late fee included ) regarding nonpayment.\n I contacted Bank of America on each occasion and was informed that it was an error on their end.\n I contacted customer service on XX/XX/XXXX to inform them of nonpayment from my escrow account.\n I was informed that this would be escalated and paid immediately.\n I checked my online account on XX/XX/XXXX to see if the payment had been made.\n The payment had not been submitted and I contacted customer once again.\n I was informed that the payment had not been paid and a manager would call me back."
# complaint_classification_sample_input = dcc.Textarea(
#         id='textarea-1',
#         value=complaint_classification_sample_text,
#         style={'width': '100%', 'height': 200},
#     )
review_classification_sample_text = " My room was dirty and I was afraid to walk barefoot on the floor which looked as if it was not cleaned in weeks\n White furniture which looked nice in pictures was dirty too and the door looked like it was attacked by an angry dog\n My shower drain was clogged and the staff did not respond to my request to clean it\n On a day with heavy rainfall a pretty common occurrence in Amsterdam the roof in my room was leaking luckily not on the bed you could also see signs of earlier water damage\n I also saw insects running on the floor\n Overall the second floor of the property looked dirty and badly kept\n On top of all of this a repairman who came to fix something in a room next door at midnight was very noisy as were many of the guests I understand the challenges of running a hotel in an old building but this negligence is inconsistent with prices demanded by the hotel On the last night after I complained about water damage the night shift manager offered to move me to a different room but that offer came pretty late around midnight when I was already in bed and ready to sleep"
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
                dbc.InputGroupText("Try typing your own complaint and click on Classify consumer complaints or use the button Fetch another complaint"),
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

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.H2("Hotel Reviews classification"),
                        html.Div(review_classification_input),
                        html.Div(review_classification_button),
                        # html.Div(id='container-button-classification'),
                        html.Div(reviews_classification_output_figure),
                        # html.Div(review_classification_sample_input),
                        ],
                        width=6
                    ),
                    dbc.Col(
                        children=[
                        html.H2("Consumer complaints classification"),
                        html.Div(complaint_classification_input),
                        complaints_buttons,
                        # html.Div(complaint_classification_button),
                        # html.Div(fetch_complaint_button),
                        # html.Div(id='container-button-classification'),
                        html.Div(complaints_classification_output_figure),
                        # html.Div(complaint_classification_sample_input),
                        ],
                        width=6
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
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

def classify_complaints(text: str):
    syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    use_model = watson_nlp.load(watson_nlp.download('embedding_use_en_stock'))
    if text is None:
        return empty_output
    else:        
        syntax_result = syntax_model.run(text)
        # run SVM model on top of syntax result
        svm_preds = complaints_svm_model.run(use_model.run(syntax_result, doc_embed_style='raw_text'))
        predicted_svm = svm_preds.to_dict()
        return predicted_svm

    # ensemble_preds = complaints_ensemble_model.run(text)
    # # predicted_ensemble = ensemble_preds.to_dict()["classes"][0]["class_name"]
    # predicted_ensemble = ensemble_preds.to_dict()
    # return predicted_ensemble

@app.callback(
    # Output('container-button-classification', 'children'),
    Output('reviews-classification-output-figure', 'figure'),
    Input('reviews-classification-button', 'n_clicks'),
    State('reviews-classification-input', 'value')
)
def reviews_classification_callback(n_clicks, value):
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
    fig_classification.update_layout(template=plotly_template,barmode='stack',title_text='Hotel Review Classification', title_x=0.5)
    return fig_classification

@app.callback(
    Output('complaints-classification-output-figure', 'figure'),
    # Input('fetch-complaint-button', 'n_clicks'),
    Input('complaints-classification-input', 'value')
)
def complaints_classification_callback(value):
    classification_output_python = classify_complaints(value)
    # print("OUTPUT CLASSES: ", classification_output_python['classes'])

    df_classification = pd.DataFrame(classification_output_python['classes'])
    # Adding a column with colors
    # df_classification["color"] = np.where(df_classification["class_name"]=='Complaint', 'red', 'green')

    # Plot for sentiment score
    fig_classification = go.Figure()
    fig_classification.add_trace(
        go.Pie(
            name='Consumer complaint category',
            values=df_classification['confidence'],
            labels=df_classification['class_name'],
            # marker_color=df_classification['color'],
            # hovertext=df_classification['Text']
            ))
    fig_classification.update_layout(template=plotly_template,barmode='stack',title_text='Consumer complaints Classification', title_x=0.5)
    return fig_classification

@app.callback(
    Output('complaints-classification-input', 'value'),
    Input('fetch-complaint-button', 'n_clicks'),
)
def fetch_complaint_from_dataset(n_clicks):
    print("n_clicks", complaints_df.values[n_clicks])
    return complaints_df.values[n_clicks]

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8051, debug=True)
