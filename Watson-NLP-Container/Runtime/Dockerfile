#*****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39"
FROM ${WATSON_RUNTIME_BASE} as base
#################
## Build Phase ##
#################
FROM base as build

# Args for artifactory credentials
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_API_KEY
ENV ARTIFACTORY_USERNAME=${ARTIFACTORY_USERNAME}
ENV ARTIFACTORY_API_KEY=${ARTIFACTORY_API_KEY}

# Build arg to specify space-delimited names of models
ARG MODEL_NAMES
WORKDIR /app/models
# Download all of the models locally to /app/models
RUN true && \
    mkdir -p /app/models && \
    arr=(${MODEL_NAMES}) && \
    for model_name in "${arr[@]}"; do \
        python3 -c "import watson_nlp; watson_nlp.download('${model_name}', parent_dir='/app/models')"; \
    done && \
    true

###################
## Release Phase ##
###################
FROM base as release

ENV LOCAL_MODELS_DIR=/app/models
COPY --from=build /app/models /app/models
