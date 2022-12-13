# ***************************************************************** #
# (C) Copyright IBM Corporation 2022.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
ARG WATSON_RUNTIME_BASE="cp.icr.io/cp/ai/watson-nlp-runtime:1.0.18"
ARG EMOTION_MODEL="cp.icr.io/cp/ai/watson-nlp_classification_ensemble-workflow_lang_en_tone-stock:1.0.6"

FROM ${EMOTION_MODEL} as model
RUN ./unpack_model.sh

FROM ${WATSON_RUNTIME_BASE} as release

RUN true && \
    mkdir -p /app/models

ENV LOCAL_MODELS_DIR=/app/models
COPY --from=model app/models /app/models
