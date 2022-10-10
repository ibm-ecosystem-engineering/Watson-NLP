#*****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
import sys
from turtle import textinput
from GrpcClient import GrpcClient

#Getting user input
try:
    textInput=sys.argv[1]
    if(not len(textInput.strip())):
        print("Input string is required")
        quit()
except:
    print("Input string is required")
    quit()

client = GrpcClient()

#Calling the emotion analysis model
response = client.call_emotion_model(textInput)
print(response)


