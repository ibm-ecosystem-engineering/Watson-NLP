FROM python:3.9
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ARG SERVICE_PORT=8050
ENV GRPC_SERVER_URL "localhost:8085"
ENV SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL "sentiment_document-cnn-workflow_en_stock"
ENV EMOTION_CLASSIFICATION_STOCK_MODEL "ensemble-classification-wf-en-emotion-stock-predictor"
ENV NLP_MODEL_SERVICE_TYPE="mm-vmodel-id"
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION python
ENV SERVICE_PORT ${SERVICE_PORT}
EXPOSE ${SERVICE_PORT}

COPY ./*.py /app
COPY ./assets /app/assets
CMD ["python3","Emotion_dash_app.py"]
