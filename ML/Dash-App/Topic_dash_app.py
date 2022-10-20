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
from dateutil import relativedelta

plt.switch_backend('Agg') 

external_stylesheets = ['assets/bootstrap.min.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'Watson NLP - Topic Modeling'

# Setting theme for plotly charts
plotly_template = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

DATA_PATH = pathlib.Path(__file__).parent.resolve()
FILENAME = "data/complaints_downsampled.csv"
GLOBAL_DF = pd.read_csv(DATA_PATH.joinpath(FILENAME), header=0)
"""
We are casting the whole column to datetime to make life easier in the rest of the code.
It isn't a terribly expensive operation so for the sake of tidyness we went this way.
"""
GLOBAL_DF["Date received"] = pd.to_datetime(
    GLOBAL_DF["Date received"], format="%Y-%m-%d"
)

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
                style={"textDecoration": "bold", "marginRight": "20%"},
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
                    dbc.Row(html.H4("Topic Modeling: Bank Customer Complaints", style={'textAlign': 'center'}),
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

# topic_button = html.Div(
#     [
#         dbc.Button(
#             "Get Topics by company", id="topics-button", className="me-2", n_clicks=0
#         ),
#         dbc.Button("Data Source URL: Consumer Complaint Database", id="data-source", color="link", className="me-1",
#                      href="https://www.consumerfinance.gov/data-research/consumer-complaints/"),
#     ]
# )

keywords_button = html.Div(
    [
        dbc.Button(
            "Get Keywords", id="keywords-button", className="me-2", n_clicks=0
        ),
    ]
)

topic_output_figure = dcc.Graph(id='topic-output-figure')
keywords_output_figure = dcc.Graph(id='keywords-output-figure')
# keywords_output_figure = html.Img(id='keywords-output-figure')
# phrases_output_figure = html.Img(id='phrases-output-figure')
# phrases_output_figure = dcc.Graph(id='phrases-output-figure')

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

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'black',
    'fontWeight': 'bold',
    'fontSize': 24,
    "color": "grey"
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'fontSize': 24
}

WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("Most frequently extracted topics in complaints")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-frequencies",
                            # children=[dcc.Graph(id="frequency_figure")],
                            children=topic_output_figure,
                            type="default",
                        ), md=6
                    ),
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Phrases", style=tab_style, selected_style=tab_selected_style,
                                        children=[
                                            dcc.Loading(
                                                id="phrases-treemap",
                                                children=[dcc.Graph(id='phrases-output-figure')],
                                                # children=phrases_output_figure,
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Keywords", style=tab_style, selected_style=tab_selected_style,
                                        children=[
                                            dcc.Loading(
                                                id="Keywords-treemap",
                                                # children=[
                                                #     dcc.Graph(id="bank-wordcloud")
                                                # ],
                                                children=keywords_output_figure,
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=6,
                    ),
                ]
            )
        ]
    ),
]

LEFT_COLUMN = dbc.Container(
    [
        html.H4(children="Select bank & dataset size", className="display-5"),
        html.Hr(className="my-2"),
        html.Label("Select percentage of dataset", className="lead"),
        html.P(
            "(Lower is faster. Higher is more precise)",
            style={"fontSize": 10, "fontWeight": "lighter"},
        ),
        dcc.Slider(
            id="n-selection-slider",
            min=1,
            max=100,
            step=1,
            marks={
                0: "0%",
                10: "",
                20: "20%",
                30: "",
                40: "40%",
                50: "",
                60: "60%",
                70: "",
                80: "80%",
                90: "",
                100: "100%",
            },
            value=20,
        ),
        html.Label("Select time frame", className="lead"),
        html.Div(
            dcc.RangeSlider(min=GLOBAL_DF['Date received'].min().year, max=GLOBAL_DF['Date received'].max().year, id="time-window-slider"), style={"marginBottom": 10}),
        html.P(
            "(You can define the time frame down to month granularity)",
            style={"fontSize": 10, "fontWeight": "lighter"},
        ),
    ]
)

TOP_BANKS_PLOT = [
    dbc.CardHeader(html.H5("Top 10 banks by number of complaints")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-banks-hist",
                children=[
                    dbc.Alert(
                        "Not enough data to render this plot, please adjust the filters",
                        id="no-data-alert-bank",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dcc.Graph(id="bank-sample"),
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),
]

def make_marks_time_slider(mini, maxi):
    """
    A helper function to generate a dictionary that should look something like:
    {1420066800: '2015', 1427839200: 'Q2', 1435701600: 'Q3', 1443650400: 'Q4',
    1451602800: '2016', 1459461600: 'Q2', 1467324000: 'Q3', 1475272800: 'Q4',
     1483225200: '2017', 1490997600: 'Q2', 1498860000: 'Q3', 1506808800: 'Q4'}
    """
    step = relativedelta.relativedelta(months=+1)
    start = datetime.datetime(year=mini.year, month=1, day=1)
    end = datetime.datetime(year=maxi.year, month=maxi.month, day=30)
    ret = {}

    current = start
    while current <= end:
        current_str = int(current.timestamp())
        if current.month == 1:
            ret[current_str] = {
                "label": str(current.year),
                "style": {"fontWeight": "bold"},
            }
        elif current.month == 4:
            ret[current_str] = {
                "label": "Q2",
                "style": {"fontWeight": "lighter", "fontSize": 7},
            }
        elif current.month == 7:
            ret[current_str] = {
                "label": "Q3",
                "style": {"fontWeight": "lighter", "fontSize": 7},
            }
        elif current.month == 10:
            ret[current_str] = {
                "label": "Q4",
                "style": {"fontWeight": "lighter", "fontSize": 7},
            }
        else:
            pass
        current += step
    # print(ret)
    return ret

def sample_data(dataframe, float_percent):
    """
    Returns a subset of the provided dataframe.
    The sampling is evenly distributed and reproducible
    """
    print("making a local_df data sample with float_percent: %s" % (float_percent))
    return dataframe.sample(frac=float_percent, random_state=1)

def calculate_bank_sample_data(dataframe, sample_size, time_values):
    """ TODO """
    print(
        "making bank_sample_data with sample_size count: %s and time_values: %s"
        % (sample_size, time_values)
    )
    if time_values is not None:
        min_date = time_values[0]
        max_date = time_values[1]
        dataframe = dataframe[
            (dataframe["Date received"] >= min_date)
            & (dataframe["Date received"] <= max_date)
        ]
    company_counts = dataframe["Company"].value_counts()
    company_counts_sample = company_counts[:sample_size]
    values_sample = company_counts_sample.keys().tolist()
    counts_sample = company_counts_sample.tolist()

    return values_sample, counts_sample

def time_slider_to_date(time_values):
    """ TODO """
    min_date = datetime.datetime.fromtimestamp(time_values[0]).strftime("%c")
    max_date = datetime.datetime.fromtimestamp(time_values[1]).strftime("%c")
    print("Converted time_values: ")
    print("\tmin_date:", time_values[0], "to: ", min_date)
    print("\tmax_date:", time_values[1], "to: ", max_date)
    return [min_date, max_date]

def get_complaint_count_by_company(dataframe):
    """ Helper function to get complaint counts for unique banks """
    company_counts = dataframe["Company"].value_counts()
    # we filter out all banks with less than 11 complaints for now
    company_counts = company_counts[company_counts > 10]
    values = company_counts.keys().tolist()
    counts = company_counts.tolist()
    return values, counts

def make_options_bank_drop(values):
    """
    Helper function to generate the data format the dropdown dash component wants
    """
    ret = []
    for value in values:
        ret.append({"label": value, "value": value})
    return ret

app.layout = html.Div(children=[
                navbar_main,
                dbc.Row(
                    [
                        dbc.Col(LEFT_COLUMN, md=4, align="center"),
                        dbc.Col(dbc.Card(TOP_BANKS_PLOT), md=8),
                    ],
                    style={"marginTop": 30},
                ),
                html.Br(),
                dbc.Row(
                    [
                    dbc.Col(
                        children=[
                        html.H4(children="Topic Modeling on 5 randomly selected Banks", className="display-5"),
                        html.Label("Select a bank from the dropdown", className="lead"),
                        dcc.Dropdown(["Discover Bank", "Navient Solutions, LLC.", "Synchrony Financial", "Paypal Holdings, Inc ", "Ocwen Financial Corporation"], "Discover Bank", id='bank-dropdown',style={'color':'#00361c'}),
                        #html.Div(topic_modeling_input),
                        # html.Div(topic_button),
                        # html.Div(id='container-button-topic'),
                        dbc.Card(WORDCLOUD_PLOTS),
                        # html.Div(topic_output_figure),
                        # html.Div(topic_output_table),
                        # html.H3("Most Frequent Keywords & Phrases of top 5 Topics"),
                        # html.Div(phrases_output_figure),
                        # html.Div(keywords_output_figure),
                        ],
                        # width=6
                    ),
                    # dbc.Col(
                    #     children=[
                    #         html.Div(phrases_output_figure),
                    #     ]
                    # )
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
    #Output('container-button-topic', 'children'),
    Output('topic-output-figure', 'figure'),
    # Output('keywords-output-figure', 'src'),
    # Output('phrases-output-figure', 'src'),
    Output('phrases-output-figure', 'figure'),
    Output('keywords-output-figure', 'figure'),
    # Output('topic-output-table', 'data'),
    # Input('topics-button', 'n_clicks'),
    Input('bank-dropdown', 'value'),
)
def topic_modeling_callback(value):
    company_topic_model = select_model(value)

    # Convert topic_dict into data frame to see which are the most imprtnat topics with Keywords & Phrases & SENTENSES (SORT BY Percentage)
    # after load the model need to be pass here as a JSON summary
    topic_df = pd.DataFrame(extract_topics_information(company_topic_model.model.to_json_summary()))
    topic_df=topic_df.sort_values("Percentage",ascending=True)

    # Plot for topics
    fig_topic = px.bar(topic_df, y="Topic Name", x=["Percentage"], orientation='h')
    fig_topic.update_layout(template=plotly_template,barmode='stack',title_text='Topic Modeling output for the Selected Bank', title_x=0.5,
                                yaxis_title="Topic Name", xaxis_title="Percentage")
    # print(topic_df[['Topic Name', 'Sentences']].head())
    # Plot for keywords
    # keywords = topic_df['Keywords'].head(5)
    # phrases = topic_df['Phrases'].head(5)
    # topic_names_val = topic_df['Topic Name'].head(5)
    # keywords_list =create_keywords_dict(keywords)
    # phrases_list =create_keywords_dict(phrases)
    # fig_keywords = plot_wordcloud_top10_topics(keywords_list,list(topic_names_val))
    # fig_phrases = plot_wordcloud_top10_topics(phrases_list,list(topic_names_val))

    # df_topic_output = topic_df[['Topic Name', 'Sentences']]
    df_topic_output['Topic Name'] = topic_df['Topic Name']
    df_topic_output['Sentences'] = topic_df['Sentences'].astype(str)
    # print("df_topic_output", df_topic_output.head())

    # Hierarchical Treemap
    fig_treemap_keywords = px.treemap(
        topic_df.explode('Keywords'),
        title="Keywords associated with the Topics",
        path=["Topic Name", "Keywords"],
        # color="Percentage",
        # color_continuous_scale=px.colors.sequential.GnBu,
    )
    fig_treemap_keywords.update_layout(template=plotly_template)
    fig_treemap_keywords.update_traces(hovertemplate='%{label}<br>%{value}<extra></extra>')
    
    fig_treemap_phrases = px.treemap(
        topic_df.explode('Phrases'),
        title="Phrases associated with the Topics",
        path=["Topic Name", "Phrases"],
        # color="Percentage",
        # color_continuous_scale=px.colors.sequential.GnBu,
    )
    fig_treemap_phrases.update_layout(template=plotly_template)
    fig_treemap_phrases.update_traces(hovertemplate='%{label}<br>%{value}<extra></extra>')


    # return fig_topic,  "data:image/png;base64,{}".format(fig_keywords), "data:image/png;base64,{}".format(fig_phrases), \
    #         df_topic_output.to_dict('records')

    return fig_topic,  fig_treemap_phrases, fig_treemap_keywords
            # df_topic_output.to_dict('records')

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

@app.callback(
    [
        Output("time-window-slider", "marks"),
        Output("time-window-slider", "min"),
        Output("time-window-slider", "max"),
        Output("time-window-slider", "step"),
        Output("time-window-slider", "value"),
    ],
    [Input("n-selection-slider", "value")],
)
def populate_time_slider(value):
    """
    Depending on our dataset, we need to populate the time-slider
    with different ranges. This function does that and returns the
    needed data to the time-window-slider.
    """
    value += 0
    min_date = GLOBAL_DF["Date received"].min()
    max_date = GLOBAL_DF["Date received"].max()

    marks = make_marks_time_slider(min_date, max_date)
    min_epoch = list(marks.keys())[0]
    max_epoch = list(marks.keys())[-1]

    return (
        marks,
        min_epoch,
        max_epoch,
        (max_epoch - min_epoch) / (len(list(marks.keys())) * 3),
        [min_epoch, max_epoch],
    )
'''
@app.callback(
    Output("bank-drop", "options"),
    [Input("time-window-slider", "value"), Input("n-selection-slider", "value")],
)
def populate_bank_dropdown(time_values, n_value):
    """ TODO """
    print("bank-drop: TODO USE THE TIME VALUES AND N-SLIDER TO LIMIT THE DATASET")
    if time_values is not None:
        pass
    n_value += 1
    bank_names, counts = get_complaint_count_by_company(GLOBAL_DF)
    counts.append(1)
    return make_options_bank_drop(bank_names)
'''
@app.callback(
    [Output("bank-sample", "figure"), Output("no-data-alert-bank", "style")],
    [Input("n-selection-slider", "value"), Input("time-window-slider", "value")],
)
def update_bank_sample_plot(n_value, time_values):
    """ TODO """
    print("redrawing bank-sample...")
    print("\tn is:", n_value)
    print("\ttime_values is:", time_values)
    if time_values is None:
        return [{}, {"display": "block"}]
    n_float = float(n_value / 100)
    bank_sample_count = 10
    local_df = sample_data(GLOBAL_DF, n_float)
    min_date, max_date = time_slider_to_date(time_values)
    values_sample, counts_sample = calculate_bank_sample_data(
        local_df, bank_sample_count, [min_date, max_date]
    )
    data = [
        {
            "x": values_sample,
            "y": counts_sample,
            "text": values_sample,
            "textposition": "auto",
            "type": "bar",
            "name": "",
        }
    ]
    layout = {
        "autosize": False,
        "margin": dict(t=10, b=10, l=40, r=0, pad=4),
        "xaxis": {"showticklabels": False},
        "template": plotly_template,
    }
    print("redrawing bank-sample...done")
    return [{"data": data, "layout": layout}, {"display": "none"}]

if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8051")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True, dev_tools_hot_reload=False)
