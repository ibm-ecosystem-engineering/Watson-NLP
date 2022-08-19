# Embed Watson NLP in a Python Web Application
This directory contains code for a web application that performs Sentiment Analysis and Emotion Classification on user-specified texts. In this application the Python code directly depends on the Watson NLP library.  Built-in pre-trained models are used.  We demonstrate how to containerize this application to ease deployment.

Note that we use the Watson NLP serving runtime as a base image. The Watson NLP library comes with it, and therefore does not need to be separately installed. 

The application contains the below files
```
├── Dockerfile
├── Sentiment_dash_app.py
├── assets
│   ├── bootstrap.min.css
│   └── ibm_logo.png
├── readme.md
└── requirements.txt
```
- Dockerfile : To create docker image
- requirements.txt :  The list of Python libraries required to run the application
- Sentiment_dash_app.py : Python program

### Prerequisites

- Docker is installed in your workstation
- Artifactory user name and API key is required to build the Docker image.  Set the following variables in your environment.
- - ARTIFACTORY_USERNAME
- - ARTIFACTORY_API_KEY

### Code snippet calling the models
Here is a code fragment from *Sentiment_dash_app.py* demonstrating how built-in models are loaded and used for scoring.
```
import watson_nlp

def get_sentiment(text):
    # load Model 
    sentiment_model = watson_nlp.load(watson_nlp.download('sentiment_document-cnn-workflow_en_stock'))
    # run the sentiment model on the result of the syntax analysis
    sentiment_output_python = sentiment_model.run(text, sentence_sentiment=True)
    return sentiment_output_python, sentiment_output_python.to_dict()['label']

def get_emotion(text):
    # Load the Emotion workflow model for English
    emotion_model = watson_nlp.load(watson_nlp.download('ensemble_classification-wf_en_emotion-stock'))
    emotion_output_python = emotion_model.run(text)
    return emotion_output_python
```

## Building the Application 

Make sure you are in the root dictory of the project where the docker file resides before you execute the below command.
```
docker build . \
  --build-arg ARTIFACTORY_USERNAME=$ARTIFACTORY_USERNAME \
  --build-arg ARTIFACTORY_API_KEY=$ARTIFACTORY_API_KEY \
  -t dash-app:latest
```
## Run the Application 
To start the container on your local machine with Docker:
```
docker run -p 8050:8050 dash-app:latest
```
You can now access the application at:
```
http://localhost:8050
```
