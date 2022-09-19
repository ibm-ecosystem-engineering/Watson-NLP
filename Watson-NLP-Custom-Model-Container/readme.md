## Serving Custom Models with a Standalone Container
In a previous tutorial, we saw how to build a standalone container image for serving stock Watson NLP models. In this tutorial, we turn our attention to serving custom models using a standalone container image. 

In this tutorial you will learn how to take a model that you have trained in Watson Studio, and build a standalone Docker container image to serve the model. As with standalone images built using stock Watson NLP models, this container image can be deployed in many environments (Docker, Kubernetes, OpenShift, cloud container services).  In this tutorial you will deploy the container image on your laptop with Docker. 

When the container runs, it exposes an endpoint that clients can use to run inference queries against the served models.  

### Architecture diagram

<diagram>
    
### Resources:
  
GitHub Repo: https://github.com/ibm-build-labs/Watson-NLP/tree/main/Watson-NLP-Container
    
### Prerequisites
    
- Docker is installed on your workstation
- Python >= 3.9 installed in your workstation to run the client program
- An IBM Artifactory username and API key are required to build the Docker image. Set the following variables in your environment.
    - ARTIFACTORY_USERNAME
    -  ARTIFACTORY_API_KEY
## Steps
### 1. Clone the git repo
Clone the git repository containing our example code.  Go to the directory that contains the code used in this tutorial. 
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
```
cd Watson-NLP-Custom-Model-Container/Runtime 
```
In this directory, you will find a Dockerfile and a models directory.   
```
% ls 
Dockerfile        models 
```
### 2. Save the Model
If you have trained a model in a Watson Studio notebook, then in this step you will export it and copy it in to the models directory.  If you do not have a model, then you can use the model that exists in the models directory to complete this tutorial. 

Before you can export your custom model, you need to ensure that a project token is set in the notebook environment so that your notebook can access the Cloud Object Storage (COS) bucket associated with the project.  

Get your access token from the IBM Data Platform GUI from Manage -> Access control -> Access tokens. 

<diagram>
Add the token to your notebook by clicking More -> Insert project token from the notebook action bar. By running the inserted hidden code cell, a project object is created that you can use to access project resources. 
<diagram>
Get your project id from Manage -> General -> Project Id 
<diagram>
Ensure that project access token is be inserted at the top of the notebook in a code cell.  Replace the project_id and project_access_token in the following with the values you have found above. 
```
from project_lib import Project 
project = Project(project_id='<project_id>', project_access_token='<project_access_token>') 
```
In your notebook environment you can save your model as a project asset by running the following. 
- <file_name> is the exported model name 
- <trained_model_object> is the model being saved

The model will be saved in a Cloud Object Storage (COS) bucket that is associated with the project in a ZIP archive.  Note that the ZIP archive created by the save_data function is compatible to the watson_nlp.load() function that is also used to load stock Watson NLP models.  

You can find the saved model in asset tab. 
<diagram>
Use the Watson Studio GUI to download the model to your work station, copying it in to the models directory. You can save multiple models in this directory.  

The file name for the model will be used as the model ID.  When making an inference request from a client program, this model ID will be used to specify which model to use. 

### 3. Build
After the models you want to serve have been saved to your workstation, you can build the container image.  Examine the contents of the Dockerfile. 
```
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39" 
FROM ${WATSON_RUNTIME_BASE} as base 
ENV LOCAL_MODELS_DIR=/app/models 
COPY models /app/models 
```

The image uses the Watson NLP Runtime image as the base image, and the models are copied in to the container file system.  A default version of the Runtime is set in the Dockerfile, but this can be overridden in the build command. 

Build the image using the following command. 
```
docker build . \ 
--build-arg WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39" \ 
-t watson-nlp-custom-container:v1 
```
This results in a image named watson-nlp-custom-container:v1. 
### 4. Run 
Use the following command to start the server with Docker on your local machine. 
```
docker run -d -p 8085:8085 watson-nlp-custom-container:v1 
```
The container exposes a gRPC service on port 8085. 

### 5. Test 
We will test the service using a simple Python client program.  The client code is under the directory Watson-NLP-Custom-Model-Container/Client.  Assuming we start in the Runtime directory: 
```
cd ../Client 
```
Ensure that the Watson NLP Python SDK is installed on your machine. 
```
pip3 install watson_nlp_runtime_client 
```
The client command expects a single text string argument, and requests inference scoring of by one of the models being served.  Run the client command as: 
```
python3 client.py "Watson NLP is awesome" 
```

This will query the default model that we have packaged with this example.  In order to query another model, you will have to update some of the client code. 
To make call to the gRPC inference service, you will need the following: 

- Model ID.   This is passed as a header argument, mm-model-id : “<MODEL_ID>”. You can set the Model ID in environment variable 
```
export WATSON_NLP_MODEL_ID=” ensemble_classification-wf_en_emotion” 
```
- Make a request object based on the model id. You may have to pass additional parameter. 
```
request = common_service_pb2.watson_nlp_topics_Message( 
    raw_document=dm.RawDocument(text=inputText).to_proto() 
) 
```
- Call the stub installed by Watson_nlp_runtime_client 
```
response = self.stub.watson_nlp_topics_Predict(request,metadata=[("mm-model-id", WATSON_NLP_MODEL_ID)] ) 
```
