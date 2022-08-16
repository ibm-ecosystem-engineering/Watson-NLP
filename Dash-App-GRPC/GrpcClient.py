import os
import grpc
import syntax_types_pb2
import common_service_pb2_grpc as CommonServiceStub
import common_service_pb2 as CommonService

class GrpcClient:
    # default constructor
    def __init__(self):
        GRPC_SERVER_URL = os.getenv("GRPC_SERVER_URL", default="127.0.0.1:8033")
        print("###### Calling GRPC endpoint = ", GRPC_SERVER_URL)
        channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = CommonServiceStub.CommonServiceStub(channel)

     # a method calling syntax_izumo_en_stock model
    def call_syntax_izumo(self, inputText):
        request = CommonService.watson_nlp_blocks_syntax_izumo_IzumoTextProcessing_Request(
            raw_document=syntax_types_pb2.RawDocument(text=inputText)
        )   
        SYNTAX_IZUMO_EN_STOCK_MODEL = os.getenv("SYNTAX_IZUMO_EN_STOCK_MODEL", default="syntax-izumo-en-stock-predictor")
        print("###### Calling remote GRPC model = ", SYNTAX_IZUMO_EN_STOCK_MODEL)
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
        print("###### Calling remote GRPC model = ", SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL)
        response = self.stub.watson_nlp_workflows_document_sentiment_cnn_CNN_Predict(request,metadata=[("mm-vmodel-id", SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL)] )
        return response

    # emotion analysis ensemble_classification-wf_en_emotion-stock
    def call_emotion_model(self, inputText):
        request = CommonService.watson_nlp_workflows_classification_ensemble_Ensemble_Request(
            raw_document=inputText
        )
        EMOTION_CLASSIFICATION_STOCK_MODEL = os.getenv("EMOTION_CLASSIFICATION_STOCK_MODEL", default="ensemble-classification-wf-en-emotion-stock-predictor")
        print("###### Calling remote GRPC model = ", EMOTION_CLASSIFICATION_STOCK_MODEL)
        response = self.stub.watson_nlp_workflows_classification_ensemble_Ensemble_Predict(request,metadata=[("mm-vmodel-id", EMOTION_CLASSIFICATION_STOCK_MODEL)] )
        return response
