# Serving a Custom Model on a Kubernetes or OpenShift Cluster
In this tutorial you will take a Watson NLP model that you have trained in Watson Studio and serve it on a Kubernetes or OpenShift cluster. The model will be packaged as a container image using the [model builder](https://github.com/IBM/ibm-watson-embed-model-builder). The container images can be used in the same way as the pretrained Watson NLP models, i.e. specified as init containers of Watson NLP Runtime Pods.

To complete this tutorial, you need to have first completed the [Consumer Complaint Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, which includes steps on training a custom ensemble model and saving it to the Cloud Object Storage (COS) bucket associated with the project.

### Prerequisites
    
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- Docker has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#docker)
- You have a Kubernetes or OpenShift cluster on which you can deploy an application
- You have either the Kubernetes (`kubectl`) or OpenShift (`oc`) CLI installed, and logged into your cluster. The current namespace should be set to the namespace in which you will deploy the model service
- Your Kubernetes or OpenShift cluster has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)
- You have completed the [Consumer Complaint Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, and have saved the custom trained model named `ensemble_model` to the COS bucket associated with the project. The tutorial uses this [notebook](https://github.com/ibm-build-labs/Watson-NLP/blob/main/ML/Text-Classification/Consumer%20complaints%20Classification.ipynb). 
    
## Steps

### 1. Save your model
First, you will export your Watson NLP model from Watson Studio on IBM Cloud. Create a `models` directory on your local machine.
```
mkdir models
```
In the IBM Cloud Pak for Data GUI, navigate to the page for your Consumer Complaints Classification project. Click on the **Assets** tab. There you should find a model named `ensemble_mode` stored as a ZIP archive. 

If the model is not there, go back to the notebook and ensure that you have followed the steps in the notebook:
  - Insert a project token into the notebook, and
  - Run the cell that saves the model.
```
project.save_data('ensemble_model', data=ensemble_model.as_file_like_object(), overwrite=True)
```

Download the model into the *models* directory on your local machine. Use the vertical ellipsis to the right of the model name to open a menu with the download option. Ensure that you use the file name `ensemble_model` when saving the file.

### 2. Build the model image

Install the [model builder](https://github.com/IBM/ibm-watson-embed-model-builder) package.
```
pip install watson-embed-model-packager
```
Run the setup for the model builder package.
```
python -m watson_embed_model_packager setup \
    --library-version watson_nlp:3.2.0 \
    --local-model-dir /path/to/models \
    --output-csv model-manifest.csv
```
Ensure that you replace `/path/to/models` in the above command with the path to your `models` directory.  This command will generate the file `model-manifest.csv` that will be used during the build.

Run the build command.
```
python -m watson_embed_model_packager build --config model-manifest.csv
```
This will create a Docker image with the name `watson-nlp_ensemble_model`. 

Verify the existence of this image:
```
docker images
```

### 3. Copy the model to a container registry

To deploy this image in Kubernetes or OpenShift cluster, you must first provision the image to a container repository.  Tag your image with proper repository and namespace/project name. Replace `<REGISTRY>` and `<NAMESPACE>` in the following commands based on your configuration.
```
docker tag watson-nlp_ensemble_model:v1 <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:v1 
```
Push the image to the registry.
```
docker push <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:v1 
```

### 4. Serve the models

Clone the GitHub repository containing sample code for this tutorial.
```
git clone https://github.com/ibm-build-labs/Watson-NLP
```
Go to the directory for this tutorial.
```
cd Watson-NLP/MLOps/custom-model-k8s
```
Open the Kubernetes manifest for editing.
```
vim Runtime/deployment/deployment.yaml
```
Update the init container line in the file to point to your custom model image.
```
    spec:
      initContainers:
      - name: ensemble-model
        image: <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:v1
```

Create a secret in the namespace to give credentials to the registry used, and add this secret to the `imagePullSecrets` section, so that your Pod can pull the image from the registry. 

Deploy the model service.  

If using Kubernetes:
```
kubectl apply -f deployment/deployment.yaml
```
If using OpenShift:
```
oc apply -f deployment/deployment.yaml
```
The model service is now deployed. 

### 5. Test the service
Run a simple Python client program to test that the model is being served. Note that the client code is specific to the model. If you serve a different model you will need to update the client program.

Install the Python client library on your machine. 
```
pip install watson_nlp_runtime_client 
```
Enable port forwarding from your local machine. 

If running the service in a Kubernetes cluster:
```
kubectl port-forward svc/watson-nlp-runtime-service 8085 
```
For OpenShift:
```
oc port-forward svc/watson-nlp-runtime-service 8085
```
Go to the directory with the client program and run it.   
```
cd client
```
Run the program with a single string argument.
```
python client.py "Watson NLP is awesome" 
```
The program will return output similar to the following.
```
###### Calling GRPC endpoint =  localhost:8085
###### Calling remote GRPC model =  ensemble_model
classes {
  class_name: "Credit reporting, credit repair services, or other personal consumer reports"
  confidence: 0.328219473
}
classes {
  class_name: "Debt collection"
  confidence: 0.262635
}
classes {
  class_name: "Credit card or prepaid card"
  confidence: 0.16425848
}
classes {
  class_name: "Checking or savings account"
  confidence: 0.102090739
}
classes {
  class_name: "Mortgage"
  confidence: 0.0733666793
}
producer_id {
  name: "Voting based Ensemble"
  version: "0.0.1"
}
```
