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
import watson_nlp
# import time

# start_time = time.time()

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
                    dbc.Row(html.H4("Sentiment & Emotion Classification", style={'textAlign': 'center'}),
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

sentiment_sample_text = "I don't share everyone's unbridled enthusiasm for this film. It is indeed a great popcorn flick, with outstanding aerial photography and maneuvers. But 10 stars? There are few, if any, movies that are perfect, and deserve that kind of rating. \
The problem with the film is the plot. It is so filled with age-worn cliches that one could easily tell what was coming from beginning to end. I mean, you had to know who was going to save the day at the end, and you had to know what was going to happen when Maverick jumped out of Penny's window. Those are just two examples of the many obvious plot points that you could see coming a mile away. I could list them all, but it would take up too much space here. Basically the entire plot was entirely predictable. \
The opening scene, especially, was straight out of Hollywood Screenplay Writing 101. I mean, seriously, how many times have we seen that subplot? Countless. \
There were no characters in the movie, either. They were all caricatures, stereotypes. No depth to any of them. They had their standard roles to play, and that was it. \
Did I enjoy the film? Sure, it was fun. Especially on a big theater screen with a loud sound system. Did I take anything away from the film? Did it make me think about anything after it was over? Nah. Will I see it again? Nah. \
I will give Tom Cruise credit for including Val Kilmer in the cast. Considering his health problems, that was a nice touch. \
So, yeah, enjoy the film. Sit back with your bag of popcorn and enjoy the g-forces. But don't pretend it is anything other than just another summer blockbuster."
# sentiment_sample_input = dcc.Textarea(
#         id='textarea-sentiment',
#         value=sentiment_sample_text,
#         style={'width': '100%', 'height': 200},
#     )
sentiment_sample_input = dbc.InputGroup(
            [
                dbc.InputGroupText("Example Text for Sentiment Analysis"),
                dcc.Textarea(
                    id='textarea-sentiment',
                    value=sentiment_sample_text,
                    style={'width': '100%', 'height': 100},
                ),
                dcc.Clipboard(
                    target_id="textarea-sentiment",
                    title="copy",
                    style={
                        # "position": "absolute",
                        # "top": 0,
                        # "right": 20,
                        # "fontSize": 20,
                        # "color": "black",
                        # "display": "inline-block",
                        # "verticalAlign": "top",
                    },
                ),
            ],
            # className="mb-3",
)
emotion_sample_text = " Rooms were stunningly decorated and really spacious in the top of the building Pictures are of room 300 The true beauty of the building has been kept but modernised brilliantly Also the bath was lovely and big and inviting Great more for couples Restaurant menu was a bit pricey but there were loads of little eatery places nearby within walking distance and the tram stop into the centre was about a 6 minute walk away and only about 3 or 4 stops from the centre of Amsterdam Would recommend this hotel to anyone it s unbelievably well priced too"
# emotion_sample_input = dcc.Textarea(
#         id='textarea-emotion',
#         value=emotion_sample_text,
#         style={'width': '100%', 'height': 200},
#     )
emotion_sample_input = dbc.InputGroup(
            [
                dbc.InputGroupText("Example Text for Emotion Classification"),
                dcc.Textarea(
                    id='textarea-emotion',
                    value=emotion_sample_text,
                    style={'width': '100%', 'height': 100},
                ),
                dcc.Clipboard(
                    target_id="textarea-emotion",
                    title="copy2",
                    style={
                        "position": "absolute",
                        "top": 0,
                        "right": 20,
                        "color": "black",
                        "display": "inline-block",
                        "fontSize": 20,
                        "verticalAlign": "top",
                    },
                ),
            ],
            # className="mb-3",
)

sentiment_analysis_input =  dbc.InputGroup(
            [
                dbc.InputGroupText("Enter Text for Sentiment Analysis"),
                dbc.Textarea(id="sentiment-input", placeholder="Text for Sentiment analysis"),
                dcc.Clipboard(
                    target_id="textarea-sentiment",
                    title="copy1",
                    style={
                        "display": "inline-block",
                        "fontSize": 20,
                        "verticalAlign": "top",
                        "color": "black"
                    },
                ),
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
        dbc.Button(id="sentiment-result", color="success", className="me-1"),
    ]
)

emotion_button = html.Div(
    [
        dbc.Button(
            "Get Emotion", id="emotion-button", className="me-2", n_clicks=0
        ),
        dbc.Button(id="emotion-result", color="success", className="me-1"),
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

empty_sentiment_output = {
  "score": 0,
  "label": "Sentiment not analyzed",
  "mixed": "NONE/EMPTY",
  "target": "",
  "sentiment_mentions": [
    {
      "span": {
        "begin": 0,
        "end": 0,
        "text": "NONE/EMPTY"
      },
      "score": 0,
      "label": "NONE/EMPTY"
    },
  ],
  "producer_id": {
    "name": "Document BERT Sentiment",
    "version": "0.0.1"
  }
}

# start_time_sentiment = time.time()
sentiment_model = watson_nlp.load('models/bert_wkflow_imdb_5_epochs')
# sentiment_model = watson_nlp.download_and_load('sentiment-aggregated_cnn-workflow_en_stock')
# print("SENTIMENT MODEL LOADING TIME--- %s seconds ---" % (time.time() - start_time_sentiment))

def get_sentiment(text):
    # load Model 
    # sentiment_model = watson_nlp.load(watson_nlp.download('sentiment_document-cnn_en_stock'))
    # sentiment_model = watson_nlp.load('models/bert_wkflow_imdb_5_epochs')
    # sentiment_model = watson_nlp.download_and_load('sentiment-aggregated_bert-workflow_en_stock')
    # syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    # run the syntax model
    # syntax_result = syntax_model.run(text, parsers=('token', 'lemma', 'part_of_speech'))
    # run the sentiment model on the result of the syntax analysis
    # sentiment_output_python = sentiment_model.run(syntax_result, sentence_sentiment=True)
    sentiment_output_python = ''
    if text is None:
        return empty_sentiment_output['sentiment_mentions'], empty_sentiment_output['label'], empty_sentiment_output['score']
    else:
        sentiment_output_python = sentiment_model.run(text, sentence_sentiment=True, language_code="en")
        sentence_sentiment = sentiment_output_python.to_dict()['sentiment_mentions']
        # sentence_label = sentiment_output_python.to_dict()['label']
        document_sentiment_label = sentiment_output_python.to_dict()['label']
        document_sentiment_score = sentiment_output_python.to_dict()['score']
        print("sentiment_output_python######", sentiment_output_python)
        # return sentiment_output_python, sentiment_output_python.to_dict()['label']
        return sentence_sentiment, document_sentiment_label, document_sentiment_score

empty_emotion_output = {
  "classes": [
    {
      "class_name": "Emotion not analyzed",
      "confidence": 0
    },
  ],
  "producer_id": {
    "name": "Voting based Ensemble",
    "version": "0.0.1"
  }
}

emotion_model = watson_nlp.download_and_load('ensemble_classification-wf_en_emotion-stock')

def get_emotion(text):
    # Load the Emotion workflow model for English
    # emotion_model = watson_nlp.load('models/ensemble_classification-wf_en_emotion-stock')
    # emotion_model = watson_nlp.download_and_load('ensemble_classification-wf_en_emotion-stock')
    if text is None:
        return empty_emotion_output
    else:
        emotion_output_python = emotion_model.run(text)
        print("EMOTION ####", emotion_output_python)
        return emotion_output_python.to_dict()

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
                        html.H4("Sentiment Analysis"),
                        html.Div(sentiment_analysis_input),
                        html.Div(sentiment_button),
                        html.Div(id='container-button-sentiment'),
                        html.Div(sentiment_output_figure),
                        html.Div(sentiment_output_table),
                        html.Div(sentiment_sample_input),
                        ],
                        width=6
                    ),
                    dbc.Col(
                        children=[
                        html.H4("Emotion Classification"),
                        html.Div(emotion_classification_input),
                        html.Div(emotion_button),
                        html.Div(id='container-button-emotion'),
                        html.Div(emotion_output_figure),
                        html.Div(emotion_output_table),
                        html.Div(emotion_sample_input),
                        ],
                        width=6
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
                html.Br(),
                html.Footer(children="Please note that this content is made available by IBM Build Lab to foster Embedded AI technology adoption. \
                                The content may include systems & methods pending patent with USPTO and protected under US Patent Laws. \
                                Copyright - 2022 IBM Corporation")
])

@app.callback(
    # Output('container-button-sentiment', 'children'),
    Output('sentiment-result', 'children'),
    Output('sentiment-output-figure', 'figure'),
    Output('sentiment-output-table', 'data'),
    Input('sentiment-button', 'n_clicks'),
    State('sentiment-input', 'value')
)
def sentiment_analysis_callback(n_clicks, value):
    # start_time = time.time()
    # sentiment_output_example_processed = json.dumps(sentiment_output_example)
    sentiment_output = get_sentiment(value)
    # sentence_sentiment = get_sentiment(value)[0]
    # print("sentence_sentiment: ****", sentence_sentiment)
    # sentence_sentiment = [(sm['score']) for sm in sentence_sentiment]
    sentence_sentiment = [(sm['score']) for sm in sentiment_output[0]]
    # sentence_sentiment = [(sm['score']) for sm in sentiment_output_python.to_dict()['sentiment_mentions']]

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
    fig_sentiment.update_layout(template=plotly_template,barmode='stack',title_text='Sentence Sentiment Score', title_x=0.5,
                                xaxis_title="Sentence Number", yaxis_title="Sentiment Score")
    

    # sentiment_output_python = json.loads(sentiment_output_example)
    # sentence_sentiment = get_sentiment(value)[0]
    sentence_sentiment = sentiment_output[0]
    sentence_sentiment = [(sm['span']['text'], sm['label'], sm['score']) for sm in sentence_sentiment]
    # sentence_sentiment = [(sm['span']['text'], sm['label'], sm['score']) for sm in sentiment_output_python.to_dict()['sentiment_mentions']]
    # print("OUTPUT LENGTH:", len(sentence_sentiment))
    # print("DATAFRAME  SHAPE:", df_sentiment_output['Sentence'].shape)
    sentence_list = []
    label_list = []
    score_list = []
    # print("#### ", sentence_sentiment)
    for sent_outputs in sentence_sentiment:
        sentence_list.append(sent_outputs[0])
        label_list.append(sent_outputs[1])
        score_list.append(sent_outputs[2])
    df_sentiment_output.drop(df_sentiment_output.index, inplace=True)
    # print("DATAFRAME: ", df_sentiment_output)    
    df_sentiment_output['Sentence'] = sentence_list
    df_sentiment_output['Label'] = label_list
    df_sentiment_output['Score'] = score_list

    # print("SENTIMENT CALLBACK TIME--- %s seconds ---" % (time.time() - start_time))
    return ("Overall Sentiment Output: ", sentiment_output[1], ' | ', str(round(sentiment_output[2], 2))), \
        fig_sentiment, df_sentiment_output.to_dict('records')

@app.callback(
    # Output('container-button-emotion', 'children'),
    Output('emotion-result', 'children'),
    Output('emotion-output-figure', 'figure'),
    Output('emotion-output-table', 'data'),
    Input('emotion-button', 'n_clicks'),
    State('emotion-input', 'value')
)
def update_output(n_clicks, value):
    # start_time = time.time()
    # emotion_output_python = json.loads(emotion_output_example)
    emotion_output_python = get_emotion(value)
    class_name_list = []
    confidence_list = []
    for classes in emotion_output_python['classes']:
    # for classes in emotion_output_python.to_dict()['classes']:
        class_name_list.append(classes['class_name'])
        confidence_list.append(classes['confidence'])
    df_emotion.drop(df_emotion.index, inplace=True)
    df_emotion['class_name'] = class_name_list
    df_emotion['confidence'] = confidence_list
    print("df_emotion: ", df_emotion)

    fig_emotion = px.bar(df_emotion, x='class_name', y='confidence')
    fig_emotion.update_layout(template=plotly_template,barmode='stack',title_text='Emotion Score', title_x=0.5,
                                xaxis_title="Emotion", yaxis_title="Confidence Score")
    # print("EMOTION CALLBACK TIME--- %s seconds ---" % (time.time() - start_time))
    return ("Prominent Emotion : ", emotion_output_python['classes'][0]['class_name'], ' | ', str(round(emotion_output_python['classes'][0]['confidence'], 2))),\
         fig_emotion, df_emotion.to_dict('records')

# print("TOTAL APP TIME--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8050")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)
    # app.run(host="0.0.0.0", port=8051, debug=True)
