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

# Load a syntax model to split the text into sentences and tokens
syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
# Load bilstm model in WatsonNLP
bilstm_model = watson_nlp.load(watson_nlp.download('entity-mentions_bilstm_en_stock'))
# Load rbr model in WatsonNLP
rbr_model = watson_nlp.load(watson_nlp.download('entity-mentions_rbr_en_stock'))
# Load bert model in WatsonNLP
bert_model = watson_nlp.load(watson_nlp.download('entity-mentions_bert_multi_stock'))
# Load transformer model in WatsonNLP
#transformer_model = watson_nlp.load(watson_nlp.download('entity-mentions_transformer_multi_stock'))

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

def extract_entities(data, model, hotel_name=None, website=None):
    import html

    input_text = str(data)
    text = html.unescape(input_text)
    if model == 'rbr':
        # Run rbr model on text
        mentions = rbr_model.run(text)
    else:
        # Run syntax model on text 
        syntax_result = syntax_model.run(text)
        if model == 'bilstm':
            # Run bilstm model on syntax result
            mentions = bilstm_model.run(syntax_result)
        elif model == 'bert':
            # Run bert model on syntax result
            mentions = bert_model.run(syntax_result)
        '''
        elif model == 'transformer':
            # Run transformer model on syntax result
            mentions = transformer_model.run(syntax_result)
        '''
            
    entities_list = mentions.to_dict()['mentions']
    ent_list=[]
    for i in range(len(entities_list)):
        ent_type = entities_list[i]['type']
        ent_text = entities_list[i]['span']['text'] 
        ent_list.append({'ent_type':ent_type,'ent_text':ent_text})
        
    if len(ent_list) > 0:
        return {'Document':text,'Hotel Name':hotel_name,'Website':website,'Entities':ent_list}
    else:
        return {}

def clean(doc):
    import html

    wnlp_stop_words = watson_nlp.download_and_load('text_stopwords_classification_ensemble_en_stock').stopwords
    stop_words = list(wnlp_stop_words)
    stop_words.remove('keep')
    stop_words.extend(["gimme", "lemme", "cause", "'cuz", "imma", "gonna", "wanna", 
                    "gotta", "hafta", "woulda", "coulda", "shoulda", "howdy","day", 
                    "first", "second", "third", "fourth", "fifth", "London", "london", 
                    "1st", "2nd", "3rd", "4th", "5th", 
                    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", 
                    "weekend", "week", "evening", "morning"])
    # replacing &amp to & as it is HTML tag
    stop_free = " ".join([html.unescape(word) for word in doc.split() if word.lower() not in stop_words])
    return stop_free

def run_extraction(df, text_col):
    extract_list = []
    all_text = dict(zip(df[text_col], zip(df['hotel'], df['website'])))
    all_text_clean = {clean(doc[0]): doc[1] for doc in all_text.items()}
    for text in all_text_clean.items():
        # change the second parameter to 'rbr', 'bilstm', or 'bert' to try other models
        extract_value = extract_entities(text[0], 'bilstm', text[1][0], text[1][1])
        if len(extract_value) > 0:
            extract_list.append(extract_value)              
    return extract_list

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
    Output('entity-output-table', 'data'),
    Input('entity-button', 'n_clicks'),
    State('entity-input', 'value')
)
def text_entity_callback(n_clicks, value):
    entities_dict = extract_entities(value, 'bilstm')
    entities_df = pd.DataFrame(entities_dict['Entities']).rename(columns={'ent_type':'Entity Type', 'ent_text':'Entity Text'})
    return entities_df

@app.callback(
    Output('hotel-entities-figure', 'figure'),
    Output('hotel-types-figure', 'figure'),
    Input('hotel-button', 'n_clicks'),
    Input('hotel-dropdown', 'value'),
)
def hotel_reviews_entity_callback(n_clicks, value):
    if value == 'Belgrave':
        df = pd.read_csv('hotel-reviews/uk_england_london_belgrave_hotel.csv')
    elif value == 'Euston':
        df = pd.read_csv('hotel-reviews/uk_england_london_euston_square_hotel.csv')
    elif value == 'Dorset':
        df = pd.read_csv('hotel-reviews/uk_england_london_dorset_square.csv')

    extract_list = run_extraction(df, 'text')
    analysis_df = pd.DataFrame(columns=['Document','Hotel Name', 'Website', 'Entities'])
    analysis_df = analysis_df.append(extract_list,ignore_index = True)
    exp_entities = analysis_df.explode('Entities')
    entities_df = pd.concat([exp_entities.drop('Entities', axis=1), exp_entities['Entities'].apply(pd.Series)], axis=1)
    hotel_name = entities_df['Hotel Name'][0]
    entities_df['ent_text'].value_counts().head(20).sort_values().plot(kind='barh', title=hotel_name + ' Entities')
    entities_df['ent_type'].value_counts().head(20).sort_values().plot(kind='barh', title=hotel_name + ' Entity Types')
    entities_fig = px.bar(entities_df['ent_text'].value_counts().head(20).sort_values(), 
                            orientation='h', 
                            title=hotel_name + ' Entities', 
                            labels={
                                "index":"Top 20 Entities",
                                "value":"Count",
                                "variable":"Legend"
                            })
    types_fig = px.bar(entities_df['ent_type'].value_counts().head(20).sort_values(), 
                        orientation='h', 
                        title=hotel_name + ' Entity Types', 
                        labels={
                            "index":"Top 20 Entities",
                            "value":"Count",
                            "variable":"Legend"
                        })
    return entities_fig, types_fig

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
