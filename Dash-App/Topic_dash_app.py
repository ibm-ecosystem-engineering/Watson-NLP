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
app.title = 'Watson NLP - Topic Modeling'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]


navbar_main = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                    dbc.Col(html.Img(src=app.get_asset_url('ibm_logo.png'), height="30px")),
                    dbc.Col(dbc.NavbarBrand("Build Lab", className="me-auto")),
                    ],
                    align="center",
                    className="w-0",
                ),
                style={"textDecoration": "bold", "margin-right": "20%"},
            ),
            dbc.Row(html.H2("Watson NLP: "),
            className="me-auto",
            justify='center',
            ),
            dbc.Row(html.H3("Topic Modeling"),
            className="me-auto",
            justify='center'
            ),
            dbc.Row(
                [
                        dbc.Nav(
                            [
                                dbc.NavItem(
                                    dbc.NavLink("©"),
                                    # add an auto margin after this to push later links to end of nav
                                    className="me-auto",
                                ),
                                # html.Span(dcc.LogoutButton(logout_url='https://w3.ibm.com/w3publisher/ibm-build-labs'), className="ml-auto")
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

# Extracting all Topic names , Keywords , Phrases & Sentences from the Topic Model
def extract_topics_information(topic_model_output):
    topic_dict=[]
    for topic in topic_model_output['clusters']:
        topic_val = {'Topic Name':topic['topicName'],'Total Documents':topic['numDocuments'],'Percentage':topic['percentage'],'Cohesiveness':topic['cohesiveness'],'Keywords':topic['modelWords'],'Phrases':topic['modelNgram'],'Sentences':topic['sentences']}
        # print("------------", topic['sentences'])
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

def plot_wordcloud_top10_topics(keywords_list,topic_names):
    cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'
    cloud = WordCloud(background_color='white',width=150,height=100,max_words=10,colormap='tab10',
                  color_func=lambda *args, **kwargs: cols[i],
                  prefer_horizontal=1.0)
    fig, axes = plt.subplots(1,5, figsize=(25,10), sharex=True, sharey=True)
    for i, ax in enumerate(axes.flatten()):
        ax.set_title(topic_names[i])
        fig.add_subplot(ax)
        topic_words = keywords_list[i]
        cloud.generate_from_frequencies(topic_words, max_font_size=50)
        buf = io.BytesIO() # in-memory files
        plt.imshow(cloud,interpolation='bilinear')
        #plt.set_title(topic_names[i], fontdict=dict(size=16))
        # fig.update_layout(title_text=topic_names[i], title_x=0.5)
        # fig.update_layout(template=plotly_template)
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.margins(x=0, y=0)
    plt.tight_layout()
    # print('plotting cloud')
    plt.savefig(buf, format = "png", dpi=72, bbox_inches = 'tight', pad_inches = 0) # save to the above file object
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()
    return data

'''
app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.Div([topic_modeling_input, topic_button, keywords_button]),
                        html.Div(id='container-button-topic'),
                        html.Div(topic_output_figure),
                        html.Div(keywords_output_figure),
                        html.Div(phrases_output_figure),
                        ],
                        width=6
                    ),
                    ],
                    # align="center",
                    # className="w-0",
                ),
])
'''
app.layout = html.Div(children=[
                    navbar_main,
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        dcc.Dropdown(["Discover Bank", "Navient Solutions, LLC.", "Synchrony Financial", "Paypal Holdings, Inc ", "Ocwen Financial Corporation"], "Discover Bank", id='bank-dropdown',style={'color':'#00361c'}),
                        #html.Div(topic_modeling_input),
                        html.Div(topic_button),
                        # html.Div(id='container-button-topic'),
                        html.Div(topic_output_figure),
                        html.Div(topic_output_table),
                        html.H3("Most Frequent Keywords & Phrases of top 5 Topics"),
                        html.Div(keywords_output_figure),
                        html.Div(phrases_output_figure),
                        ],
                        # width=6
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
    #Output('container-button-topic', 'children'),
    Output('topic-output-figure', 'figure'),
    Output('keywords-output-figure', 'src'),
    Output('phrases-output-figure', 'src'),
    Output('topic-output-table', 'data'),
    Input('topics-button', 'n_clicks'),
    Input('bank-dropdown', 'value'),
)
def topic_modeling_callback(n_clicks, value):
    company_topic_model = select_model(value)

    # Convert topic_dict into data frame to see which are the most imprtnat topics with Keywords & Phrases & SENTENSES (SORT BY Percentage)
    # after load the model need to be pass here as a JSON summary
    topic_df = pd.DataFrame(extract_topics_information(company_topic_model.model.to_json_summary()))
    topic_df=topic_df.sort_values("Percentage",ascending=False)

    # Plot for topics
    fig_topic = px.bar(topic_df, x="Topic Name", y=["Percentage"])
    fig_topic.update_layout(template=plotly_template,barmode='stack',title_text='Topic Modeling output for the Selected Company', title_x=0.5,
                                xaxis_title="Topic Name", yaxis_title="Percentage")
    # print(topic_df[['Topic Name', 'Sentences']].head())
    # Plot for keywords
    keywords = topic_df['Keywords'].head(5)
    phrases = topic_df['Phrases'].head(5)
    topic_names_val = topic_df['Topic Name'].head(5)
    keywords_list =create_keywords_dict(keywords)
    phrases_list =create_keywords_dict(phrases)
    fig_keywords = plot_wordcloud_top10_topics(keywords_list,list(topic_names_val))
    fig_phrases = plot_wordcloud_top10_topics(phrases_list,list(topic_names_val))

    # df_topic_output = topic_df[['Topic Name', 'Sentences']]
    df_topic_output['Topic Name'] = topic_df['Topic Name']
    df_topic_output['Sentences'] = topic_df['Sentences'].astype(str)
    # print("df_topic_output", df_topic_output.head())

    return fig_topic,  "data:image/png;base64,{}".format(fig_keywords), "data:image/png;base64,{}".format(fig_phrases), \
            df_topic_output.to_dict('records')

def select_model(value):
    if value == "Discover Bank":
        return watson_nlp.load('models/complaint_topic_model_discover/')
    elif value == "Navient Solutions, LLC.":
        return watson_nlp.load('models/complaint_topic_model_navient/')
    elif value == "Synchrony Financial":
        return watson_nlp.load('models/complaint_topic_model_synchrony/')
    elif value == "Paypal Holdings, Inc":
        return watson_nlp.load('models/complaint_topic_model_paypal/')
    elif value == "Ocwen Financial Corporation":
        return watson_nlp.load('models/complaint_topic_model_ocwen/')
    else:
        return watson_nlp.load('models/complaint_topic_model_discover/')

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8051")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)
