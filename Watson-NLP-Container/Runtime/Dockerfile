#*****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.20.0"
ARG SENTIMENT_MODEL="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp_sentiment_aggregated-cnn-workflow_lang_en_stock:2.8.0"
ARG EMOTION_MODEL="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp_classification_ensemble-workflow_lang_en_tone-stock:2.3.1"

FROM ${SENTIMENT_MODEL} as model1
RUN ./unpack_model.sh

FROM ${EMOTION_MODEL} as model2
RUN ./unpack_model.sh

FROM ${WATSON_RUNTIME_BASE} as release

RUN true && \
    mkdir -p /app/models

ENV LOCAL_MODELS_DIR=/app/models
COPY --from=model1 app/models /app/models
COPY --from=model2 app/models /app/models
