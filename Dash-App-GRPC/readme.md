### Watson NLP gRPC Python Client dashapp
# Build lab
This is an example Python application that uses the gRPC API to do scoring for Watson NLP models. The model serving runtime exposes GRPC endpoints to consume the model serving. As GRPC is portable, you can implement client with your choice of programming languages. Here I am going to show you how to implement an example dash app using python.

Frist of all lets generate a client stub using the proto files
Gathering Proto files to generate the full protobuf stack, proto files from a few places are required:
- The common-service definition from this repository.
- The WNLP interface definitions
- The Watson Core interface definitions

### Install the required library to generate client stub.
#### gRPC library
```
python -m pip install grpcio
```
#### gRPC tools library
```
python -m pip install grpcio-tools
```
### Generate stub
```
python3 -m grpc_tools.protoc -I ${PROTO_FILE_DIR} --python_out=${OUTPUT_DIR} --grpc_python_out=${OUTPUT_DIR} proto/*
```
### A sample GRPC client code
- ######  Create a gRPC channel
- ######  Creat a request object
- ######  Call the model by passing model id

In this sample app three models are being called
- ###### sentiment_document-cnn-workflow_en_stock
- ###### ensemble_classification-wf_en_emotion-stock
- ###### syntax_izumo_en_stock
```
import os
import grpc
import syntax_types_pb2
import common_service_pb2_grpc as CommonServiceStub
import common_service_pb2 as CommonService

class GrpcClient:
    # default constructor
    def __init__(self):
        GRPC_SERVER_URL = os.getenv("GRPC_SERVER_URL", default="127.0.0.1:8033")
        channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = CommonServiceStub.CommonServiceStub(channel)

     # a method calling syntax_izumo_en_stock model
    def call_syntax_izumo(self, inputText):
        request = CommonService.watson_nlp_blocks_syntax_izumo_IzumoTextProcessing_Request(
            raw_document=syntax_types_pb2.RawDocument(text=inputText)
        )   
        SYNTAX_IZUMO_EN_STOCK_MODEL = os.getenv("SYNTAX_IZUMO_EN_STOCK_MODEL", default="syntax-izumo-en-stock-predictor")
        response = self.stub.watson_nlp_blocks_syntax_izumo_IzumoTextProcessing_Predict(request, metadata=[("mm-vmodel-id", SYNTAX_IZUMO_EN_STOCK_MODEL)])
        return response

    # a method calling sentiment_document-cnn-workflow_en_stock
    def call_sentiment_document_workflow(self, inputText):
        request = CommonService.watson_nlp_workflows_document_sentiment_cnn_CNN_Request(
            raw_document=syntax_types_pb2.RawDocument(text=inputText),
            sentence_sentiment=True,
            show_neutral_scores=True
        )
        SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL = os.getenv("SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL", default="sentiment-document-cnn-workflow-en-stock-predictor")
        #response = self.stub.watson_nlp_workflows_sentiment_cnn_CNN_Predict(request,metadata=[("mm-vmodel-id", SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL)] )
        response = self.stub.watson_nlp_workflows_document_sentiment_cnn_CNN_Predict(request,metadata=[("mm-vmodel-id", SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL)] )
        return response

    # emotion analysis ensemble_classification-wf_en_emotion-stock
    def call_emotion_model(self, inputText):
        request = CommonService.watson_nlp_workflows_classification_ensemble_Ensemble_Request(
            raw_document=inputText
        )
        EMOTION_CLASSIFICATION_STOCK_MODEL = os.getenv("EMOTION_CLASSIFICATION_STOCK_MODEL", default="ensemble-classification-wf-en-emotion-stock-predictor")
        response = self.stub.watson_nlp_workflows_classification_ensemble_Ensemble_Predict(request,metadata=[("mm-vmodel-id", EMOTION_CLASSIFICATION_STOCK_MODEL)] )
        return response
```
### Running the code:
```
client = GrpcClient()
response = client.call_sentiment_document_workflow("Watson NLP is awesome!")
print(response)
```
### Docker file to run the dashapp
Change the environment variable according to your requirement.
```
FROM python:3.9
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ENV GRPC_SERVER_URL "localhost:8085"
ENV SYNTAX_IZUMO_EN_STOCK_MODEL "sentiment_document-cnn-workflow_en_stock"
ENV SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL "sentiment_document-cnn-workflow_en_stock"
ENV EMOTION_CLASSIFICATION_STOCK_MODEL "ensemble_classification-wf_en_emotion-stock"
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION python
EXPOSE 8050
COPY ./*.py /app
COPY ./assets /app/assets
CMD ["python3","Sentiment_dash_app.py"]
```
### Requirement file is provived to install required libraries
```
dash
dash_bootstrap_components
dash_daq
pandas
plotly
numpy
```
### building the dashapp
```
docker build -t dash-app:latest .
```
### Running the dashapp
```
docker run -p 8050:8050 dash-app:latest
```
##### You can now access the application at

```
http://localhost:8050
```
