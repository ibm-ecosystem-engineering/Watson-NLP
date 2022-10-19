import os
from pydoc import classname
from xml.dom.minidom import Document
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

# Load a syntax model to split the text into sentences and tokens
#watson_nlp.download('syntax_izumo_en_stock')
syntax_model = watson_nlp.load('syntax_izumo_en_stock')
# Load bilstm model in WatsonNLP
#watson_nlp.download('entity-mentions_bilstm_en_stock')
bilstm_model = watson_nlp.load('entity-mentions_bilstm_en_stock')
# Load noun phrases model
#watson_nlp.download('noun-phrases_rbr_en_stock')
noun_phrases_model = watson_nlp.load('noun-phrases_rbr_en_stock')
# Load keywords model 
#watson_nlp.download('keywords_text-rank_en_stock')
keywords_model = watson_nlp.load('keywords_text-rank_en_stock')
# Load sentiment model
#watson_nlp.download('targets-sentiment_sequence-bert_multi_stock')
sentiment_extraction_model = watson_nlp.load('targets-sentiment_sequence-bert_multi_stock')

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
                    dbc.Row(html.H4("Entity and Phrase Extraction", style={'textAlign': 'center'}),
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

entity_sample_text = 'I am so angry that i made this post available via all possible sites i use when planing my trips so no one will make the mistake of booking this place I made my booking via booking com We stayed for 6 nights in this hotel from 11 to 17 July Upon arrival we were placed in a small room on the 2nd floor of the hotel It turned out that this was not the room we booked I had specially reserved the 2 level duplex room so that we would have a big windows and high ceilings The room itself was ok if you don t mind the broken window that can not be closed hello rain and a mini fridge that contained some sort of a bio weapon at least i guessed so by the smell of it I intimately asked to change the room and after explaining 2 times that i booked a duplex btw it costs the same as a simple double but got way more volume due to the high ceiling was offered a room but only the next day SO i had to check out the next day before 11 o clock in order to get the room i waned to Not the best way to begin your holiday So we had to wait till 13 00 in order to check in my new room what a wonderful waist of my time The room 023 i got was just as i wanted to peaceful internal garden view big window We were tired from waiting the room so we placed our belongings and rushed to the city In the evening it turned out that there was a constant noise in the room i guess it was made by vibrating vent tubes or something it was constant and annoying as hell AND it did not stop even at 2 am making it hard to fall asleep for me and my wife I have an audio recording that i can not attach here but if you want i can send it via e mail The next day the technician came but was not able to determine the cause of the disturbing sound so i was offered to change the room once again the hotel was fully booked and they had only 1 room left the one that was smaller but seems newer '
entity_input = dbc.InputGroup(
    [
        dbc.InputGroupText("Enter Text for Entity Extraction"),
        dbc.Textarea(id="entity-input", 
                     value=entity_sample_text,
                     placeholder="Text for Entity Extraction",
                     style={'width': '100%', 'height': 300}),
    ],
    className="mb-3",
)

search_input = dbc.InputGroup(
    [
        dbc.InputGroupText("Enter entities and phrases for search (separate by commas)"),
        dbc.Textarea(id="search-input", 
                     value='clean bathroom, nice receptionist, tube station, good breakfast, great location',
                     placeholder="Entities for Search"),
    ]
)

entity_button = html.Div(
    [
        dbc.Button(
            "Get Entities", id="entity-button", className="me-2", n_clicks=0
        ),
    ]
)

hotel_button = html.Div(
    [
        dbc.Button(
            "Get Entities for hotel", id="hotel-button", className="me-2", n_clicks=0
        ),
    ]
)

phrases_button = html.Div(
    [
        dbc.Button(
            "Get Keyword phrases for hotel", id='phrases-button', className="me-2", n_clicks=0
        ),
    ]
)

search_button = html.Div(
    [
        dbc.Button(
            "Search for hotels with matching entities and phrases", id='search-button', className="me-2", n_clicks=0
        ),
    ]
)

hotel_entities_figure = dcc.Graph(id='hotel-entities-figure')
#hotel_types_figure = dcc.Graph(id='hotel-types-figure')
hotel_types_treemap = dcc.Graph(id='hotel-types-treemap')
hotel_phrases_figure = dcc.Graph(id='hotel-phrases-figure')

entities_df = pd.DataFrame(columns=['Entity Type', 'Entity Text'])
entity_output_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in entities_df.columns],
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'textAlign': 'center',
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'width': 'auto',
    },
    style_cell={
        'textAlign': 'center',
        'font-family':'sans-serif',
        'headerAlign': 'center'
    },
    style_table={
        'overflowX': 'scroll', 
        'overflowY': 'auto'
    },
    style_as_list_view=True,
    sort_action='native',
    sort_mode='multi',
    id='entity-output-table'
)

search_df = pd.DataFrame(columns=['Hotel Name', 'Document', 'phrase', 'ent_text'])
search_output_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in search_df.columns],
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'textAlign': 'center',
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'whiteSpace': 'normal',
        'color': 'white',
        'width': 'auto',
        'height': 'auto',
    },
    style_cell={
        'textAlign': 'center',
        'font-family':'sans-serif',
        'headerAlign': 'center'
    },
    style_table={
        'height': '400px', 
        'overflowX': 'scroll', 
        'overflowY': 'auto'
    },
    style_as_list_view=True,
    sort_action='native',
    sort_mode='multi',
    id='search-output-table'
)

def extract_entities(data, hotel_name=None, website=None):
    import html

    input_text = str(data)
    text = html.unescape(input_text)
    syntax_result = syntax_model.run(text)
    mentions = bilstm_model.run(syntax_result)
    entities_list = mentions.to_dict()['mentions']
    ent_list=[]
    for i in range(len(entities_list)):
        ent_type = entities_list[i]['type']
        ent_text = entities_list[i]['span']['text'] 
        ent_list.append({'ent_type':ent_type,'ent_text':ent_text})
    if len(ent_list) > 0:
        return {'Document':input_text,'Hotel Name':hotel_name,'Website':website,'Entities':ent_list}
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
        extract_value = extract_entities(text[0], text[1][0], text[1][1])
        if len(extract_value) > 0:
            extract_list.append(extract_value)
    return extract_list

def custom_tokenizer(text):
    # parse the text for pos tagging and lemmatization
    result = syntax_model.run(text, parsers=('part_of_speech', 'lemma'))

    pos_filter = {
                    4,      # POS_AUX
                    10,     # POS_PART
                    11,     # POS_PRON
                    15,     # POS_SYM
                    17      # POS_X
                  }

    # collect the terms that qualify as meaningful.
    # to qualify, a term must meet all conditions:
    # (a) not be pos-tagged as symbol / content-less word
    # (b) not be a stop-word from the pre-defined list
    # (c) be longer than 1 character
    terms = []
    for token in result.tokens:
        pos_tag = token.part_of_speech
        if pos_tag not in pos_filter:
            lemma = token.lemma.strip()
            text = token.span.text.strip()
            term = lemma if len(lemma) > 0 else text
            if len(term) >1:
                terms.append(term)
    return " ".join(terms)

def extract_keywords(text, hotel):
    # Run the Syntax and Noun Phrases models
    syntax_prediction = syntax_model.run(text, parsers=('token', 'lemma', 'part_of_speech'))
    noun_phrases = noun_phrases_model.run(text)
    # Run the keywords model
    keywords = keywords_model.run(syntax_prediction, noun_phrases, limit=5)  
    keywords_list = keywords.to_dict()['keywords']
    key_list = []
    for i in range(len(keywords_list)):
        dict_list = {}
        key = custom_tokenizer(keywords_list[i]['text'])
        dict_list['phrase'] = key
        dict_list['relevance'] = keywords_list[i]['relevance']
        key_list.append(dict_list)
    return {'Document':text,'Hotel Name':hotel,'Phrases':key_list}

def top_doc_generator(analysis_df):
    top_doc_list =[]
    for index, row in analysis_df.iterrows():
        top_doc_list.append(row['Document'])
    return top_doc_list

def explode_phrases(top_doc_list, hotel):
    keywords = [extract_keywords(doc, hotel) for doc in top_doc_list] 
    phrases_df = pd.DataFrame(keywords)

    exp_phrases = phrases_df.explode('Phrases')
    exp_phrases = exp_phrases.dropna(subset=['Phrases'])
    exp_phrases = pd.concat([exp_phrases.drop(['Phrases'], axis=1), exp_phrases['Phrases'].apply(pd.Series)], axis=1)
    exp_phrases['phrase_length'] = exp_phrases['phrase'].apply(lambda x: len(x.split(' ')))
    # Removing uni-gram and bi-grams
    exp_phrases = exp_phrases[exp_phrases.phrase_length > 2]
    return exp_phrases

def explode_phrases2(hotels_df):
    keywords = []
    for index, row in hotels_df.iterrows():
        keywords.append(extract_keywords(row['Document'], row['Hotel Name']))
    phrases_df = pd.DataFrame(keywords)

    exp_phrases = phrases_df.explode('Phrases')
    exp_phrases = exp_phrases.dropna(subset=['Phrases'])
    exp_phrases = pd.concat([exp_phrases.drop(['Phrases'], axis=1), exp_phrases['Phrases'].apply(pd.Series)], axis=1)
    exp_phrases['phrase_length'] = exp_phrases['phrase'].apply(lambda x: len(x.split(' ')))
    # Removing uni-gram and bi-grams
    exp_phrases = exp_phrases[exp_phrases.phrase_length > 2]
    return exp_phrases

def search_entity(hotels_df, entities_phrases):
    search_df = hotels_df[(hotels_df['ent_text'].str.lower().str.contains('|'.join(entities_phrases).lower())) & 
                          (hotels_df['phrase'].str.lower().str.contains('|'.join(entities_phrases).lower()))]
    search_df = search_df[['Hotel Name', 'Document', 'phrase', 'ent_text']]
    hotel_count = search_df['Hotel Name'].value_counts().to_dict()
    return search_df, hotel_count

def run_sentiment(df, text_col, ent_col):
    pos_targets =[]
    neg_targets =[]
    targets = []
    entities = dict(df[ent_col])
    for text, hotel in zip(df[text_col], df['Hotel Name']):
        syntax_analysis_en = syntax_model.run(text, parsers=('token',))
        extracted_sentiments = sentiment_extraction_model.run(syntax_analysis_en)
        for key , score in extracted_sentiments.to_dict()['targeted_sentiments'].items():
            label = score['label']
            targets.append({'Hotel Name' : hotel, 'phrase' : key, 'sentiment' : score['label']})
            if label=='SENT_POSITIVE': # and key not in pos_targets:
                pos_targets.append(key)
            elif label=='SENT_NEGATIVE': # and key not in neg_targets:
                neg_targets.append(key)
    return pos_targets, neg_targets, targets

app.layout = html.Div(children=[
                    navbar_main,
                    # Header for Section 1
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.H4(children='Searching for Hotels with Matching Entities and Phrases'),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ]
                    ),
                    # Hotel Reviews
                    dbc.Row(
                        [
                        dbc.Col(width=2,),
                        dbc.Col(
                            children=[
                                html.Div(search_input),
                                html.Div(search_button),
                                html.Div(search_output_table),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ]
                    ),
                    html.Br(),
                    # Header for Section 2
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.H4(children='Entity Extraction - Text Document'),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ]
                    ),
                    # Text input/ouput
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.Div(entity_input),
                                html.Div(entity_button),
                                html.Div(entity_output_table),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ],
                    ),
                    html.Br(),
                    # Header for Section 3
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.H4(children='The Most Common Entities in Reviews of Three Hotels'),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ]
                    ),
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                dcc.Dropdown(["Belgrave", "Euston", "Dorset"], "Belgrave", id='hotel-dropdown',style={'width':'100%', 'color':'#00361c'}),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            children=[
                                html.Div('Choose a Hotel', style={'margin-top':5})
                            ],
                            width=8),
                        ],
                    ),
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.Div(hotel_entities_figure),
                                html.Div(hotel_types_treemap),
                            ],
                            width=8,
                        ),
                        dbc.Col(width=2),
                        ],
                    ),
                    html.Br(),
                    # Header for Section 4
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                html.H4(children='The Most Relevant Phrases in Reviews of Three Hotels'),
                            ],
                            width=8, 
                        ),
                        dbc.Col(width=2),
                        ]
                    ),
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col(
                            children=[
                                dcc.Dropdown(["Belgrave", "Euston", "Dorset"], "Belgrave", id='phrases-dropdown',style={'width':'100%', 'color':'#00361c'}),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            children=[
                                html.Div('Choose a Hotel', style={'margin-top':5})
                            ],
                            width=8),
                        ],
                    ),
                    dbc.Row(
                        [
                        dbc.Col(width=2),
                        dbc.Col([
                            html.Div(hotel_phrases_figure),
                            ],
                            width=8,
                        ),
                        dbc.Col(width=2),
                        ],
                    ),
                    html.Br(),
                    html.Label("This App was built using Watson NLP library."),
                    html.Br(),
                    html.Footer(children="Please note that this content is made available by IBM Build Lab to foster Embedded AI technology adoption. \
                                    The content may include systems & methods pending patent with USPTO and protected under US Patent Laws. \
                                    Copyright - 2022 IBM Corporation")
])

@app.callback(
    Output('search-output-table', 'data'),
    Input('search-button', 'n_clicks'),
    State('search-input', 'value'),
)
def search_entity_callback(n_clicks, search_text):
    search_text = search_text.split(', ')
    compressed_hotels = pd.read_csv('hotel-reviews/compressed_hotels.csv')
    search_df, hotel_count = search_entity(compressed_hotels, search_text)
    return search_df.to_dict('records')

@app.callback(
    Output('entity-output-table', 'data'),
    Input('entity-button', 'n_clicks'),
    State('entity-input', 'value'),
)
def text_entity_callback(n_clicks, entity_input):
    entities_dict = extract_entities(entity_input)
    if len(entities_dict) > 0:
        entities_df = pd.DataFrame(entities_dict['Entities']).rename(columns={'ent_type':'Entity Type', 'ent_text':'Entity Text'})
    else:
        entities_df = pd.DataFrame([{'Entity Type': 'NONE/EMPTY', 'Entity Text': 'NONE/EMPTY'}])
    return entities_df.to_dict('records')

@app.callback(
    Output('hotel-entities-figure', 'figure'),
    #Output('hotel-types-figure', 'figure'),
    Output('hotel-types-treemap', 'figure'),
    #Input('hotel-button', 'n_clicks'),
    Input('hotel-dropdown', 'value'),
)
def hotel_reviews_entity_callback(hotel_dropdown):
    if hotel_dropdown == 'Belgrave':
        df = pd.read_csv('hotel-reviews/uk_england_london_belgrave_hotel.csv').dropna(axis=0)
    elif hotel_dropdown == 'Euston':
        df = pd.read_csv('hotel-reviews/uk_england_london_euston_square_hotel.csv').dropna(axis=0)
    elif hotel_dropdown == 'Dorset':
        df = pd.read_csv('hotel-reviews/uk_england_london_dorset_square.csv').dropna(axis=0)
    
    extract_list = run_extraction(df, 'text')
    analysis_df = pd.DataFrame(columns=['Document','Hotel Name', 'Website', 'Entities'])
    analysis_df = analysis_df.append(extract_list,ignore_index = True)
    exp_entities = analysis_df.explode('Entities')
    entities_df = pd.concat([exp_entities.drop('Entities', axis=1), exp_entities['Entities'].apply(pd.Series)], axis=1).reset_index().drop(['index'],axis=1)

    entities_fig = px.bar(entities_df['ent_text'].value_counts().head(20).sort_values(),
                            orientation='h',
                            title=hotel_dropdown + ' Entities',
                            labels={
                                "index":"Top 20 Entities",
                                "value":"Count",
                                "variable":"Legend"
                            })
    entities_fig.update_layout(template=plotly_template,barmode='stack',title_text='Entities extracted from Hotel Reviews', title_x=0.5)

    '''
    types_fig = px.bar(entities_df['ent_type'].value_counts().head(20).sort_values(),
                        orientation='h',
                        title=hotel_dropdown + ' Entity Types',
                        labels={
                            "index":"Top Entity Types",
                            "value":"Count",
                            "variable":"Legend"
                        })
    types_fig.update_layout(template=plotly_template,barmode='stack',title_text='Entity types extracted from Hotel Reviews', title_x=0.5)
    '''
    fig_treemap_types = px.treemap(
        entities_df,
        title="Entities types from Hotel Reviews",
        path=["ent_type", "ent_text"],
        color="ent_type",
        color_continuous_scale=px.colors.sequential.GnBu,
    )
    fig_treemap_types.update_layout(template=plotly_template, title_text='Entities Types from Hotel Reviews', title_x=0.5)
    return entities_fig, fig_treemap_types #types_fig, fig_treemap_types

@app.callback(
    Output('hotel-phrases-figure', 'figure'),
    #Input('hotel-button', 'n_clicks'),
    Input('phrases-dropdown', 'value'),
)
def hotel_reviews_phrases_callback(phrases_dropdown):
    import math

    if phrases_dropdown == 'Belgrave':
        df = pd.read_csv('hotel-reviews/uk_england_london_belgrave_hotel.csv').dropna(axis=0)
    elif phrases_dropdown == 'Euston':
        df = pd.read_csv('hotel-reviews/uk_england_london_euston_square_hotel.csv').dropna(axis=0)
    elif phrases_dropdown == 'Dorset':
        df = pd.read_csv('hotel-reviews/uk_england_london_dorset_square.csv').dropna(axis=0)
    
    extract_list = run_extraction(df, 'text')
    analysis_df = pd.DataFrame(columns=['Document','Hotel Name', 'Website', 'Entities'])
    analysis_df = analysis_df.append(extract_list,ignore_index = True)

    top_doc_list = top_doc_generator(analysis_df)
    exp_phrases = explode_phrases(top_doc_list, phrases_dropdown)

    lowest_rel = exp_phrases.sort_values('relevance', ascending=True).tail(20).reset_index().drop(['index'], axis=1).head(1)['relevance'][0]
    lower_bound = math.floor(lowest_rel*100)/100
    phrases_fig = px.bar(exp_phrases.sort_values('relevance', ascending=True).tail(20), 
                            x='relevance', 
                            y='phrase',
                            orientation='h', 
                            title=phrases_dropdown + 'Top Relevant Phrases Ranked',
                        )
    phrases_fig.update_xaxes(range=[lower_bound, 1.0])
    phrases_fig.update_layout(template=plotly_template,barmode='stack',title_text='Keyword phrases extracted from Hotel Reviews', title_x=0.5)
    return phrases_fig

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8051")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)
