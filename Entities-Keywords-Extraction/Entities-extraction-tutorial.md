# Easy guide to Entities, Keywords and Phrases extraction with Watson NLP

Entities, Keyword & Phrase Extraction plays major role to understand the unstructured data. These entities can include People name, Organization name, Date, Price, Facility,etc.

The `watson_nlp` library is available on IBM Watson Studio as a runtime library so that you can directly use it for model training, evaluation, and prediction. The following figure shows the Watson NLP NLP architecture.

![Architecture](images/Watson-Studio-flow.png)

IBM Watson NLP is a standard embeddable AI library that is designed to tie together the pieces of IBM Natural Language Processing. It provides a standard base natural language processing layer along with a single integrated roadmap, a common architecture, and a common code stack designed for widespread adoption across IBM products.

IBM Watson NLP now provides the ability to automatically extract entities, keywords and phrases using pre-trained models Out of the box. 

This tutorial explains the fundamentals of IBM Watson NLP and walks you through the process of extracting entities, keywords and phrases.

## Prerequisites

To follow the steps in this tutorial, you need:

* An [IBMid](https://cloud.ibm.com/login?cm_sp=ibmdev-_-developer-tutorials-_-cloudreg)
* A Watson Studio project
* A [Python notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/Emotion-Classification/Emotion%20Classification%20-%20Pre-Trained%20Models.ipynb)
* **What are the helper libraries that you need to import?**

Before working through the tutorial, you should have an understanding of IBM Watson Studio and Jupyter Notebooks.

## Estimated time

It should take you approximately 1 hour to complete this tutorial.

## Steps

The steps in this tutorial use an example of IMDB movie reviews from Kaggle to walk you through the process.

### Setting up your environment

To begin, you set up a Python notebook environment using Watson Studio on IBM Cloud so that you can use the watson_nlp_ library.

#### Reserve your env

** How does this work outside of Tech Zone when you can't reserve an env? This process needs to be documented here for people outside of IBM.**
(Note: If you can't reserve an env on Tech Zone but if you have access to Watson Studio instance, you can skip steps 1 and 2 to complete the tutorial)

1. Under the [Entities & Keywords Extraction](https://techzone.ibm.com/collection/watson-nlp-entities-keywords-extraction#tab-1) tab, find the environment tile and click **Reserve** to reserve a Watson Studio environment.

    ![reserve](images/reserve.png)

2. Shortly, you will receive an email inviting you to join an IBM cloud account. Follow the instructions in the email to join.  Your environment should be ready within a few minutes.  When it is ready, you will recieve a second email similar to the following.

    ![env_details](images/env_details.png)

3. Log in to [IBM Cloud Pak for Data](https://dataplatform.cloud.ibm.com?cm_sp=ibmdev-_-developer-tutorials-_-cloudreg). After you log in, ensure that you are using cloud account **2577353 - tsglwatson**. You can check the name of the current account on the top right of the screen.  Change the account if necessary using the drop-down menu.  From the IBM Cloud Pak for Data dashboad, find the tile for the Project that you want to work with.  For the Consumer complaints classification tutorial, the name of this Project will have the prefix **Entities-Keywords-Extraction**.  Once the Project is open, you can view the notebooks and data assets of the project using the **Assets** tab.

    (Note: If you are not using the TechZone environment, you will not have access to this IBM cloud account. You can load the [Hotel Reviews Analysis - Entities and Keywords notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/Entities-Keywords-Extraction/Hotel%20Reviews%20Analysis%20-%20Entities%20and%20Keywords.ipynb) into your Watson Studio project directly. Follow [instructions for creating notebook from URL](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.5.x?topic=notebooks-creating)).

    ![assets](images/assets.png)

4. Before working with the notebooks, you must define the environment in which these notebooks will run. To get started on that, click on the **Manage** tab.

    ![manage_tab](images/manage_tab.png)

5. Click on **Environments** from the side Navbar. Next click on **Templates** tab. Finally, click on **New template**

    ![env](images/env.png)

6. We will create an environment template that contains the Watson NLP library. Give your environment template a name like **Watson NLP**. In the Hardware configuration, select at least **4 vCPU and 16 GB RAM**  (Note: For better performance, select higher Hardware configuration). For Software, select **DO + NLP Runtime 22.1 on Python 3.9**. Finally click **Create**

    ![new_env_settings](images/new_env_settings.png)

7. Now we will set an environment for a notebook.  Click on the **Assets** tab. Find the notebook you want to work with among the assets.  Click on the ellipsis (the three dots) to the right of the notebook name in order to open a drop-down menu.  Within this menu click **Change environment**.

    ![change_env](images/change_env.png)

8. Select the environment template that you created previously and click **Change**.
 
    ![change](images/change.png)

9. You will be able to run the notebook by clicking the ellipsis and selecting **Edit**.

![edit](images/edit.png)

10. Your notebook will load. You can follow the instructions in your notebook to complete the tutorials on Watson NLP.

    ![loaded](images/loaded.png)


### Step 1. Collecting the data set

**These steps need to be broken out like the "Setting up your environment section.**
(Note: If you are reserving the env through TechZone, you don't need to collect the data manually. The env comes with the Watson Studio project pre-created for you. You can skip the rest of the steps here and follow the instructions in the notebook to complete the Text Classification tutorial. However, if you are not reserving the env through TechZone and you have a Watson Studio instance, then you should follow the steps described below)

1. The data is publicly available at [Kaggle 515K Hotel Reviews Data in Europe](https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe) and [OpinRank Review Dataset] (https://archive.ics.uci.edu/ml/datasets/OpinRank+Review+Dataset).
We will use 3 hotels for analysis and comparison and they have been saved for you on the GitHub. The data for each of the hotels can be downloaded from Github: [Hotel 1](https://github.com/ibm-build-labs/Watson-NLP/blob/main/Entities-Keywords-Extraction/uk_england_london_belgrave_hotel.csv), [Hotel 2](https://github.com/ibm-build-labs/Watson-NLP/blob/main/Entities-Keywords-Extraction/uk_england_london_dorset_square.csv), [Hotel 3](https://github.com/ibm-build-labs/Watson-NLP/blob/main/Entities-Keywords-Extraction/uk_england_london_euston_square_hotel.csv).

2. Upload the data set to your Watson Studio project by going to the Assets tab and then dropping the data files as shown in the following figure.

    ![Collecting the data set](images/collect-the-dataset.png)

3. After you have added the dataset to the project, you might have to reload the Notebook. You have two options of accessing the dataset from the Jupyter Notebook depending on the level of access you have.

    A. If you are a project administrator, then

    i) You can just insert the project token as shown below:

    ![ws-project.mov](https://media.giphy.com/media/jSVxX2spqwWF9unYrs/giphy.gif)

    ii) After inserting the project token, you can continue executing all the cells in the notebook. This cell in particular will load your dataset in the notebook.'
    ![Reading the data set using project token](images/read-data-token.png)

    B. If you are not a Watson Studio project administrator, then you cannot create a project token.

    i) Create a new cell under Step 2 - Data Loading by clicking on **Insert** menu and then selecting **Insert Cell Below** or **Esc+B** shortcut key. Highlight the code cell shown in the image below by clicking it.

    ![insert-cell.png](images/insert-cell.png)


    ii) Ensure you place the cursor below the commented line. Click the Find and add data icon (01/00) on the top right corner. Choose the Files tab, and pick the `complaint_updated.csv` file. Click Insert to code and choose pandas DataFrame. Rename the dataframe from `df_data_1` to `complaint_df`.

    ![insert-dataset.png](images/insert-dataset.png)

4. After you've added the data set to the project, you can access it from the Jupyter Notebook, and read the csv file into a pandas DataFrame.

    ![Datahead frame](images/datahead-frame.png)

### Step 3. Entity Extraction

Entity extraction uses the entity-mentions block to encapsulate algorithms for the task of extracting mentions of entities (person, organizations, dates, locations,...) from the input text. The block offers implementations of strong entity extraction algorithms from each of the four families: rule-based, classic ML, deep-learning and transformers.

There are two types of models:

A rule-based model (the rbr models), which handles syntactically regular entity types such as number, email and phone.
A model trained on labeled data for the more complex entity types such as person, organization location.

#### Step 3A. Entity extraction function

Rule-based models (rbr) do not depend on any blocks, so you can just directly run them on input text.

Models trained from labeled data, such as bilstm, bert, and transformer, depend on the Syntax block. As such, Syntax block must be run first to generate the input expected by the Entity Mention block.

1. Load the syntax model and three entity extraction models.

```
# Load a syntax model to split the text into sentences and tokens
syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
# Load bilstm model in WatsonNLP
bilstm_model = watson_nlp.load(watson_nlp.download('entity-mentions_bilstm_en_stock'))
# Load rbr model in WatsonNLP
rbr_model = watson_nlp.load(watson_nlp.download('entity-mentions_rbr_en_stock'))
# Load bert model in WatsonNLP
bert_model = watson_nlp.load(watson_nlp.download('entity-mentions_bert_multi_stock'))
```

2. Build a custom function to run a specified entity extraction model and parse its results. The returned output is a dictionary of the review text, hotel name, website, and entity mentions.

```
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
        elif model == 'transformer':
            # Run transformer model on syntax result
            mentions = transformer_model.run(syntax_result)
    
    entities_list = mentions.to_dict()['mentions']
    print(entities_list)
    ent_list=[]
    for i in range(len(entities_list)):
        ent_type = entities_list[i]['type']
        ent_text = entities_list[i]['span']['text'] 
        ent_list.append({'ent_type':ent_type,'ent_text':ent_text})
        
    if len(ent_list) > 0:
        return {'Document':input_text,'Hotel Name':hotel_name,'Website':website,'Entities':ent_list}
    else:
        return {}
```

3. Stop-words are common words that are unmeaningful for separating the data. Such common words are assumed to be "noise" as their high frequency could hide the words carrying more informative signal. We filter them based on a pre-defined list used in WatsonNLP and based on the part-of-speech. Notes:

The stop-words list can be customized for the target dataset. We demonstrate this below.
When we vectorize the documents below, we apply a filter that ignores terms that appear in 50% or more of the documents. This filter can also be counted as part of stop-words filtering.

```
wnlp_stop_words = watson_nlp.download_and_load('text_stopwords_classification_ensemble_en_stock').stopwords
stop_words = list(wnlp_stop_words)
stop_words.remove('keep')
stop_words.extend(["gimme", "lemme", "cause", "'cuz", "imma", "gonna", "wanna", 
                   "gotta", "hafta", "woulda", "coulda", "shoulda", "howdy","day", 
                   "first", "second", "third", "fourth", "fifth", "London", "london", 
                   "1st", "2nd", "3rd", "4th", "5th", 
                   "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", 
                   "weekend", "week", "evening", "morning"])
```

#### Step 3B. Run entity extraction

1. Apply data pre-processing on the input text/documents and then run the cleaned text through the model. The model used can be specified via the model parameter in extract_entities().
```
def run_extraction(df_list, text_col):
    extract_list = []
    for df in df_list:
        all_text = dict(zip(df[text_col], zip(df['hotel'], df['website'])))
        all_text_clean = {clean(doc[0]): doc[1] for doc in all_text.items()}
        for text in all_text_clean.items():
            # change the second parameter to 'rbr', 'bilstm', or 'bert' to try other models
            extract_value = extract_entities(text[0], 'bilstm', text[1][0], text[1][1])
            if len(extract_value) > 0:
                extract_list.append(extract_value)              
    return extract_list
```

2. The model will output a text's entity mention as well as its category of entity. For example, "london" mention is a Location type and "good soundproof rooms" is a Facility type.

    ![Entities extraction output](images/entities-extraction-output.png)

3. The Entities extraction model output can be visualized to analyze and understand the entities in the hotel reviews clearly.

    ![Top 20 entities](images/top-20-entities.png)


#### Step 3C. Comparing top 20 entities for each hotel
We can examine the results of the entity extraction by plotting the top frequently mentioned entities for each hotel. These mentions can be used to generate tags for a hotel to create relevancy and familiarity for search engine results.

1. Display frequency with horizontal barcharts.
    ![Entities comparison output](images/entities-comparison-output.png)


#### Step 3D. Comparison between Booking.com vs TripAdvisor for one hotel
Another approach to analyzing hotel customer reviews is by comparing the entity mentions found on the two websites where the reviews are published. Here we are looking at Booking.com vs TripAdvisor. We can hope to gain insight on the tendencies of reviewers who use one platform compared to the other platform.

1. Plot side-by-side word clouds for each of the hotels.
    ![Wordcloud comparison 1](images/comparison-wordcloud1.png)

It can be observed that the customers on Booking.com care more about the convenience to tube stations where as TripAdvisor customers care more about the reception and atmosphere of the hotel itself.

2. Similarly for the Euston hotel.
    ![Wordcloud comparison 2](images/comparison-wordcloud2.png)

We can use this collective information to give priority to the website with reviews that better align with our own preferences about choosing a hotel. Do we care more about the convenience of the location of a hotel or do we care about the hotel's ambience, reception, perks?

### Step 4. Keyword phrase extraction

Another Watson NLP capability we can utilize to analyze the hotel reviews is Keyword phrase extraction. The keywords block ranks noun phrases extracted from an input document based on how relevant they are within the document.

We will be using the text-rank model here. The text-rank model takes the output of Noun Phrase models and assigns a relevance score for each extracted noun phrase. The relevance score calculation is inspired by the Page Rank algorithm. In the context of the input document, extracted noun phrases that appear in “more connected” contexts receive a higher rank. In addition, the relevance score of extracted noun phrases is upgraded when the noun phrase appears more frequently in Wikipedia.

1. Load Noun Phrases, Embedding and Keywords models for English

    ```
    syntax_model = watson_nlp.load(watson_nlp.download('syntax_izumo_en_stock'))
    noun_phrases_model = watson_nlp.load(watson_nlp.download('noun-phrases_rbr_en_stock'))
    keywords_model = watson_nlp.load(watson_nlp.download('keywords_text-rank_en_stock'))
    ```

2. The following function captures the flow for running a keyword extraction model. First, we run the input document/text through the syntax model and the noun phrases model to extract noun texts. Then, we use both syntax output and noun output as inputs for the keyword model where the ouput will include the text phrase and relevance score. We can use this score to rank the phrases

```
def extract_keywords(text):
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
    return {'Complaint data':text,'Phrases':key_list}
```

3. Plot the result of the keyword phrase extraction for the 3 hotels.
    ![Phrase extraction plot](images/phrase-extraction-plot.png)

These top-ranked phrases can be used to generate a brief description of the most noteable attributes of each hotel. Customers can find interest in a particular hotel with just take one look at the list of phrases.

## Conclusion

This tutorial shows you how to use the Watson NLP library and how easily you can run various entity, phrase, and target sentiment extraction models on input text. This notebook also demonstrated one possible application of Watson NLP.