# Serving a Custom Model on a Kubernetes or OpenShift Cluster
In this tutorial you will take a Watson NLP model that you have trained in Watson Studio and serve it on a Kubernetes or OpenShift cluster. The model will be packaged as a container image using the [model builder](https://github.com/IBM/ibm-watson-embed-model-builder). The container images can be used in the same way as the pretrained Watson NLP models, i.e. specified as init containers of Watson NLP Runtime Pods.

To complete this tutorial, you need to have first completed the [Consumer Complaint Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, which includes steps on training a custom ensemble model and saving it to the Cloud Object Storage (COS) bucket associated with the project.

### Architecture diagram

![reference architecture](Images/reference_architecture.png)
    
### Prerequisites
    
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- Docker has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#docker)
- You have created a custom trained Watson NLP model in Watson Studio, generated using this [notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/ML/Text-Classification/Consumer%20complaints%20Classification.ipynb) 
- You have a Kubernetes or OpenShift cluster on which you can deploy an application
- You have either the Kubernetes (`kubectl`) or OpenShift (`oc`) CLI installed, and configured to talk to your cluster.
- Your Kubernetes or OpenShift cluster has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)
- You have completed the [Consumer Complaint Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, and have saved the custom trained model named `ensemble_model` to the COS bucket associated with the project. The tutorial uses this [notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/ML/Text-Classification/Consumer%20complaints%20Classification.ipynb).
    
**Tip**:
- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.  
      
    
## Steps

### 1. Save your model
First, you will export your Watson NLP model from Watson Studio on IBM Cloud. Create a `models` directory on your local machine.
```
mkdir models
```
Go to the page for your Consumer Complaints Classification project in the IBM Cloud Pak for Data GUI and click on the **Assets** tab. There you should find a model named `ensemble_mode` stored as a ZIP archive. 

If the model is not there, go back to the notebook and ensure that you have followed the steps in the notebook:
  - Insert a project token into the notebook, and
  - Run the cell that saves the model.
```
project.save_data('ensemble_model', data=ensemble_model.as_file_like_object(), overwrite=True)
```

Download the model into the *models* directory on your local machine. Use the vertical ellipsis to the right of the model name to open a menu with the download option. Ensure that you use the file name `ensemble_model` when saving the file.

### 2. Build the container image

Install the 

### 3. Serve the models

### 4. Test the service
Now test the model service using a client program on your local machine. Install the Watson NLP Runtime client library.
```
pip install watson-nlp-runtime-client
```
The client program appears in the directory `Watson-NLP/Watson-NLP-Custom-Model-Container/Client`. Note that the client code included with this tutorial will make inference requests to the sample model `ensemble_classification-wf_en_emotion-stock` that is referenced in step 2.  If you are using your own model, you will have to first update the client code.

Enable port forwarding. On Kubernetes:

OpenShift:


From the `Runtime` directory:
```
cd ../Client 
```
Run the client program.
```
python3 client.py "Watson NLP is awesome" 
```
This program takes a single text string as an argument.  The result from the model is printed to the screen.
