import os
from pydoc import classname
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

entity_input = dbc.InputGroup(
    [
        dbc.InputGroupText("Enter Text for Entity Extraction"),
        dbc.Textarea(id="entity-input", placeholder="Text for Entity Extraction"),
    ],
    className="mb-3",
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

hotel_entities_figure = dcc.Graph(id='hotel-entities-figure')
hotel_types_figure = dcc.Graph(id='hotel-types-figure')

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
    style_table={'overflowX': 'scroll'},
    style_as_list_view=True,
    sort_action='native',
    sort_mode='multi',
    id='entity-output-table'
)

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

def run_extraction(df, text_col, model):
    extract_list = []
    all_text = dict(zip(df[text_col], zip(df['hotel'], df['website'])))
    all_text_clean = {clean(doc[0]): doc[1] for doc in all_text.items()}
    for text in all_text_clean.items():
        # change the second parameter to 'rbr', 'bilstm', or 'bert' to try other models
        extract_value = extract_entities(text[0], model, text[1][0], text[1][1])
        if len(extract_value) > 0:
            extract_list.append(extract_value)              
    return extract_list

app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.Div(entity_input),
                        dcc.Dropdown(["rbr", "bilstm", "bert"], "bilstm", id='model-dropdown',style={'color':'#00361c'}),
                        html.Div(entity_button),
                        html.Div(entity_output_table),
                        dcc.Dropdown(["Belgrave", "Euston", "Dorset"], "Dorset", id='hotel-dropdown',style={'color':'#00361c'}),
                        html.Div(hotel_button),
                        html.Div(hotel_entities_figure),
                        html.Div(hotel_types_figure),
                        ],
                        width=10
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
])

@app.callback(
    Output('entity-output-table', 'data'),
    Input('entity-button', 'n_clicks'),
    State('entity-input', 'value'),
    Input('model-dropdown', 'value'),
)
def text_entity_callback(n_clicks, entity_input, model_dropdown):
    entities_dict = extract_entities(entity_input, model_dropdown)
    if len(entities_dict) > 0:
        entities_df = pd.DataFrame(entities_dict['Entities']).rename(columns={'ent_type':'Entity Type', 'ent_text':'Entity Text'})
    else:
        entities_df = pd.DataFrame([{'Entity Type': 'NONE/EMPTY', 'Entity Text': 'NONE/EMPTY'}])
    return entities_df.to_dict('records')

@app.callback(
    Output('hotel-entities-figure', 'figure'),
    Output('hotel-types-figure', 'figure'),
    Input('hotel-button', 'n_clicks'),
    Input('hotel-dropdown', 'value'),
    Input('model-dropdown', 'value'),
)
def hotel_reviews_entity_callback(n_clicks, hotel_dropdown, model_dropdown):
    if hotel_dropdown == 'Belgrave':
        df = pd.read_csv('hotel-reviews/uk_england_london_belgrave_hotel.csv').dropna(axis=0)
    elif hotel_dropdown == 'Euston':
        df = pd.read_csv('hotel-reviews/uk_england_london_euston_square_hotel.csv').dropna(axis=0)
    elif hotel_dropdown == 'Dorset':
        df = pd.read_csv('hotel-reviews/uk_england_london_dorset_square.csv').dropna(axis=0)
    
    extract_list = run_extraction(df, 'text', model_dropdown)
    analysis_df = pd.DataFrame(columns=['Document','Hotel Name', 'Website', 'Entities'])
    analysis_df = analysis_df.append(extract_list,ignore_index = True)
    exp_entities = analysis_df.explode('Entities')
    entities_df = pd.concat([exp_entities.drop('Entities', axis=1), exp_entities['Entities'].apply(pd.Series)], axis=1).reset_index().drop(['index'],axis=1)
    hotel_name = entities_df['Hotel Name'][0]
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
                            "index":"Top Entity Types",
                            "value":"Count",
                            "variable":"Legend"
                        })
    return entities_fig, types_fig

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8051, debug=True)
