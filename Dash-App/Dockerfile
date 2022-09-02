
ARG WATSON_RUNTIME_BASE=wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39
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
EXPOSE 8050
RUN groupadd appuser && adduser -g appuser appuser && usermod -aG appuser appuser
RUN chown -R appuser:appuser /app
USER appuser
COPY . /app
ENTRYPOINT ["python3","Sentiment_dash_app.py"]
