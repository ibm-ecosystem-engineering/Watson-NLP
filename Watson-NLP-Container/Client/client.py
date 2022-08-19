#*****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
from GrpcClient import GrpcClient
client = GrpcClient()
response = client.call_emotion_model("I am sad")
print(response)

sentimentResponse = client.call_sentiment_document_model_workflow("I am sad too")
print(sentimentResponse)