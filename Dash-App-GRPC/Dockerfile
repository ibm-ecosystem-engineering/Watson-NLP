FROM python:3.9
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ENV GRPC_SERVER_URL "localhost:8085"
ENV SYNTAX_IZUMO_EN_STOCK_MODEL "sentiment_document-cnn-workflow_en_stock"
ENV SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL "sentiment_document-cnn-workflow_en_stock"
ENV EMOTION_CLASSIFICATION_STOCK_MODEL "ensemble_classification-wf_en_emotion-stock"
ENV NLP_MODEL_SERVICE_TYPE="mm-model-id"
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION python
EXPOSE 8050
COPY ./*.py /app
COPY ./assets /app/assets
CMD ["python3","Sentiment_dash_app.py"]
