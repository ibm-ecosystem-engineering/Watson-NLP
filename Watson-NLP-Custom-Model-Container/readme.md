## Serving Custom Watson NLP Models using Standalone Containers
In this tutorial you will learn how to export a Watson NLP model from Watson Studio and to serve it with Docker. 

The approach taken is to create a standalone container image, in which the models are packaged into the image together with the Watson NLP Runtime.  When the container runs it will expose REST and gRPC endpoints that client programs can use to make inference requests. 

Standalone containers are useful since they can be deployed anywhere:  On your laptop using Docker; on a Kubernetes or OpenShift cluster; or on a cloud container service like IBM Code Engine or AWS Fargate.  In this tutorial, you will run the container on your local machine using Docker.

### Architecture diagram

![reference architecture](Images/reference_architecture.png)
    
### Prerequisites
    
- Docker is installed on your workstation.
- Python >= 3.9 installed in your workstation to run the client program.
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
If you have trained a model in a Watson Studio notebook, then in this step you will export it and copy it in to the models directory.  If you do not have a model, then you can download a model from [here](https://github.com/ibm-build-labs/Watson-NLP/releases/download/ml_model/ensemble_classification-wf_en_emotion) and save it in the models directory to complete this tutorial. In that case you may skip to step 3.

Before you can export your custom model, you need to ensure that a project token is set in the notebook environment so that your notebook can access the Cloud Object Storage (COS) bucket associated with the project.  

Get your access token from the IBM Data Platform GUI from **Manage -> Access control -> Access tokens.** 

![access token](Images/access_token.png)

Add the token to your notebook by clicking **More -> Insert project token** from the notebook action bar. By running the inserted hidden code cell, a project object is created that you can use to access project resources. 

![insert token](Images/insert_token.png)

Get your project id from **Manage -> General -> Project Id**

![project id](Images/project_id.png)
    
Ensure that project access token is be inserted at the top of the notebook in a code cell.  Replace the **project_id** and **project_access_token** in the following with the values you have found above. 
```
from project_lib import Project 
project = Project(project_id='<project_id>', project_access_token='<project_access_token>') 
```
In your notebook environment you can save your model as a project asset by running the following. 
- <file_name> is the exported model name 
- <trained_model_object> is the model being saved

The model will be saved in a Cloud Object Storage (COS) bucket that is associated with the project in a ZIP archive.  Note that the ZIP archive created by the save_data function is compatible to the watson_nlp.load() function that is also used to load stock Watson NLP models.  

You can find the saved model in asset tab. 

![saved model](Images/saved_model.png)
    
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
We will test the service using a simple Python client program.  The client code is under the directory **Watson-NLP-Custom-Model-Container/Client**.  Assuming we start in the Runtime directory: 
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

- **Model_ID:** This is passed as a header argument, mm-model-id : “<MODEL_ID>”. You can set the Model ID in environment variable 
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
