#*****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
import grpc
import os
import watson_nlp.data_model as dm
from watson_nlp_runtime_client import common_service_pb2, common_service_pb2_grpc

class GrpcClient:
    # default constructor
    def __init__(self):
        GRPC_SERVER_URL = os.getenv("GRPC_SERVER_URL", default="localhost:8085")
        print("###### Calling GRPC endpoint = ", GRPC_SERVER_URL)
        channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = common_service_pb2_grpc.CommonServiceStub(channel)

    # emotion analysis ensemble_classification-wf_en_emotion-stock
    def call_emotion_model(self, inputText):
        request = common_service_pb2.EmotionDocumentWorkflowRequest(
            raw_document=dm.RawDocument(text=inputText).to_proto()
        )
        EMOTION_CLASSIFICATION_STOCK_MODEL = os.getenv("EMOTION_CLASSIFICATION_STOCK_MODEL", default="ensemble_classification-wf_en_emotion")
        print("###### Calling remote GRPC model = ", EMOTION_CLASSIFICATION_STOCK_MODEL)
        response = self.stub.EmotionDocumentWorkflowPredict(request,metadata=[("mm-model-id", EMOTION_CLASSIFICATION_STOCK_MODEL)] )
        return response