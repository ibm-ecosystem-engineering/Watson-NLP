# Embed Watson NLP in a Python Web Application
This directory contains an example a Python web application.  This application performs Sentiment Analysis and Emotion Classification on user-specified texts. The Watson NLP library is directly embedded in a Python program and Watson NLP built-in models are used.  We demonstrate how to containerize this application so that it may be deployed easily anywhere.

To develop this app we need the following
- Watson nlp serving runtime
- Watson nlp libraries
- IBM entitlement key to gain access to your container software

Once you gain access to nlp serving runtime as a base image, watson nlp library comes with it. You don't have to install watson nlp library seperately.
### The required libraries
```
dash
dash_bootstrap_components
dash_daq
pandas
plotly
numpy
```
### Code snippet calling the models
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
## Build
### Update Dockerfile 
Change the environment variable according to your requirement.
```
ARG WATSON_RUNTIME_BASE=wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.9.0-ubi8_py39
FROM ${WATSON_RUNTIME_BASE} as base

# Args for artifactory credentials
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_API_KEY
ENV ARTIFACTORY_USERNAME ${ARTIFACTORY_USERNAME}
ENV ARTIFACTORY_API_KEY ${ARTIFACTORY_API_KEY}

# Setting up the working directory
WORKDIR /app

# Installing the required python library to run models
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 list
EXPOSE 8050
RUN groupadd appuser && adduser -g appuser appuser && usermod -aG appuser appuser
RUN chown -R appuser:appuser /app
USER appuser
COPY . /app
ENTRYPOINT ["python3","Sentiment_dash_app.py"]
```
### Building the dashapp
To build the above, simply put it in a Dockerfile and run the docker build command using the following example as a guide. You need to gain access to artifactory user name and api key.
- ARTIFACTORY_USERNAME
- ARTIFACTORY_API_KEY
```
docker build . \
  --build-arg ARTIFACTORY_USERNAME=$ARTIFACTORY_USERNAME \
  --build-arg ARTIFACTORY_API_KEY=$ARTIFACTORY_API_KEY \
  -t dash-app:latest
```
### Run the Application 
```
docker run -p 8050:8050 dash-app:latest
```
### You can now access the application at

```
http://localhost:8050
```
