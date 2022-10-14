# Serving a Custom Model on a Kubernetes or OpenShift Cluster

This tutorial is aimed at Data Scientists, Developers or MLOps Engineers who want to take custom trained model that has been developed in Watson Studio, and serve it on a Kubernetes or OpenShift cluster.  The approach we take is to:
  - download the model from Watson Studio,
  - package it up as a container image,
  - push the image to a container registry, and
  - serve the model on a Kubernetes or OpenShift cluster.
 
Packaging will be done using the [model builder tool](https://github.com/IBM/ibm-watson-embed-model-builder).  The model image will be packaged in the same way as are the pretrained Watson NLP models, so serving them in a Kubernetes or OpenShift cluster. This allows for a consistent deployment pattern to the one used for pretrained models: model images will be specified as init containers of Watson NLP Runtime Pods.

### Architecture diagram

![reference architecture](Images/reference_architecture.png)
    
### Prerequisites
    
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- Docker has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#docker)
- [Watson NLP Runtime Python client library](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#python) is installed
- You have created a custom trained Watson NLP model in Watson Studio, generated using this [notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/ML/Sentiment-Analysis/Sentiment%20Analysis%20-%20Model%20Training.ipynb) 
    
**Tip**:
- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.  
  
## Steps
### 1. Clone the GitHub repository
Clone the repository that contains example code used in this tutorial. 
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
Go to the build directory.
```
cd Watson-NLP/MLOps/Watson-NLP-Custom-Model-Container/Runtime 
```
You will find in this directory a `Dockerfile` and a `models` subdirectory. When we build the container image, any models that are in the `models` directory will be copied into the image.

### 2. Export your model
In this step you will export a Watson NLP model from Watson Studio on IBM Cloud.

Go to the page for your project in the IBM Cloud Pak for Data GUI. Create an access token with *Editor* role using **Manage > Access control > Access tokens** if one does not already exist.

![access token](Images/access_token.png)

Open your notebook for editing.  You need to ensure that the project token is set so that you can access the project assets from the notebook.  Look for a cell similar to the following at the top of your notebook.
```
# @hidden_cell
# The project token is an authorization token that is used to access project resources like data sources, connections, and used by platform APIs.
from project_lib import Project
project = Project(project_id='<project-id>', project_access_token='<access-token>')
pc = project.project_context
```
If you do not see this cell, then add it to the notebook by clicking **More > Insert project token** from the notebook action bar. Run the cell.

![insert token](Images/insert_token.png)
    
Add the following line to your notebook and run it in order to save your model.
```
project.save_data('<file_name>', data=<trained_model_object>.as_file_like_object(), overwrite=True)
```
Where:
- `<file_name>` is the exported model name 
- `<trained_model_object>` is the model being saved

The model will be saved as a ZIP archive in the Cloud Object Storage (COS) bucket associated with the project. Once saved, you will be able to find it in the **Assets** tab. 

![saved model](Images/saved_model.png)
    
Download the model into the *models* directory on your local machine using the file name `bert_wkflow_imdb_5_epochs`. (Use the vertical ellipsis to the right of the model name to open a menu with the download option.)

### 3. Build the container image
Have a look at the Dockerfile in the current directory.
```
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39" 
FROM ${WATSON_RUNTIME_BASE} as base 
ENV LOCAL_MODELS_DIR=/app/models 
COPY models /app/models 
```
The Watson NLP Runtime is used as the base image. Any models that are in the `models` subdirectory on the host will be opein the container at build time.

Use the following command to build the image. 
```
docker build . -t watson-nlp-custom-container:v1 
```
This results in a image named `watson-nlp-custom-container:v1`.  Check that it exists.
```
docker images
```

### 4. Run the service with Docker
Use the following command to start the service. 
```
docker run -d -p 8085:8085 watson-nlp-custom-container:v1 
```
The container will expose a gRPC endpoint on port 8085. 

### 5. Test the service
Now test the model service using a client program. Ensure that the [Watson NLP Python SDK](https://github.com/ibm-build-labs/Watson-NLP/blob/main/access/README.md) is installed on your machine.

The client program appears in the directory `Watson-NLP/Watson-NLP-Custom-Model-Container/Client`. Note that the client code included with this tutorial will make inference requests to the sample model `ensemble_classification-wf_en_emotion-stock` that is referenced in step 2.  If you are using your own model, you will have to first update the client code.

From the `Runtime` directory:
```
cd ../Client 
```
Run the client program.
```
python3 client.py "Watson NLP is awesome" 
```
This program takes a single text string as an argument.  The result from the model is printed to the screen.
