# Serving a Custom Model on a Kubernetes or OpenShift Cluster

In this tutorial you will take a Watson NLP model that you have trained in Watson Studio and serve it on a Kubernetes or OpenShift cluster. The model will be packaged as a container image using the [model builder](https://github.com/IBM/ibm-watson-embed-model-builder). The container images can be used in the same way as the pretrained Watson NLP models, i.e. specified as init containers of Watson NLP Runtime Pods.

To complete this tutorial, you need to have first completed the [Consumer Complaints Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, which includes steps on training a custom ensemble model and saving it to the Cloud Object Storage (COS) bucket associated with the project.

## Reference Architecture

![Reference architecure](Images/ref-arch-custom-models.png)

## Prerequisites

- [Python 3.9](https://www.python.org/downloads/) or later is installed
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- Docker has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-lab/Watson-NLP/blob/main/MLOps/access/README.md#docker)
- You have a Kubernetes or OpenShift cluster on which you can deploy an application
- You have either the Kubernetes (`kubectl`) or OpenShift (`oc`) CLI installed, and logged into your cluster. The current namespace should be set to the namespace in which you will deploy the model service
- Your Kubernetes or OpenShift cluster has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-lab/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)
- You have completed the [Consumer Complaints Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification#tab-1) tutorial, and have saved the custom trained model named `ensemble_model` to the COS bucket associated with the project. The tutorial uses this [notebook](https://github.com/ibm-build-lab/Watson-NLP/blob/main/ML/Text-Classification/Consumer%20complaints%20Classification.ipynb).

## Steps

### 1. Save your model

First, you will export your Watson NLP model from Watson Studio on IBM Cloud. In the IBM Cloud Pak for Data GUI, navigate to the page for your Consumer Complaints Classification project. Click on the **Assets** tab. There you should find a model named `ensemble_mode` stored as a ZIP file.

If the model is not there, go back to the notebook and ensure that you have followed the steps in the notebook:

- Insert a project token into the notebook, and
- Run the cell that saves the model.

```python
project.save_data('ensemble_model', data=ensemble_model.as_file_like_object(), overwrite=True)
```

Use the vertical ellipsis to the right of the model name to open a menu with the download option. Download the model to your local machine.

Next, we will unzip the file. Create a directory to unzip the file into.

```sh
mkdir models
```

```sh
mkdir models/ensemble_model
```

Unzip the file into the newly created directory. You may need to specify the path to the ZIP file if it is not in the current directory.

```sh
unzip ensemble_model -d models/ensemble_model
```

### 2. Build the model image

Prepare your Python environment.

```sh
python3 -m venv client-env
```

```sh
source client-env/bin/activate
```

Install the [model builder](https://github.com/IBM/ibm-watson-embed-model-builder) package.

```sh
pip install watson-embed-model-packager
```

Run the setup for the model builder package.

```sh
python -m watson_embed_model_packager setup \
    --library-version watson_nlp:3.2.0 \
    --local-model-dir /path/to/models \
    --output-csv model-manifest.csv
```

Ensure that you replace `/path/to/models` in the above command with the path to your `models` directory. This command will generate the file `model-manifest.csv` that will be used during the build.

Run the build command.

```sh
python -m watson_embed_model_packager build --config model-manifest.csv
```

This will create a Docker image with the name `watson-nlp_ensemble_model`.

Verify the existence of this image:

```sh
docker images
```

### 3. Copy the model to a container registry

To deploy this image in Kubernetes or OpenShift cluster, you must first provision the image to a container repository. Tag your image with proper repository and namespace/project name. Replace `<REGISTRY>` and `<NAMESPACE>` in the following commands based on your configuration.

```sh
docker tag watson-nlp_ensemble_model:latest <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:latest
```

Push the image to the registry.

```sh
docker push <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:latest
```

### 4. Serve the models

Clone the GitHub repository containing sample code for this tutorial.

```sh
git clone https://github.com/ibm-build-lab/Watson-NLP
```

Go to the directory for this tutorial.

```sh
cd Watson-NLP/MLOps/custom-model-k8s
```

Open the Kubernetes manifest for editing.

```sh
vim deployment/deployment.yaml
```

Update the init container line in the file to point to your custom model image.

```yaml
    spec:
      initContainers:
      - name: ensemble-model
        image: <REGISTRY>/<NAMESPACE>/watson-nlp_ensemble_model:latest
```

Create a [secret](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials) in the namespace to give credentials to the registry used, and [add this secret](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret) to the `imagePullSecrets` section, so that your Pod can pull the image from the registry.

Deploy the model service.

If using Kubernetes:

```sh
kubectl apply -f deployment/deployment.yaml
```

If using OpenShift:

```sh
oc apply -f deployment/deployment.yaml
```

The model service is now deployed.

### 5. Test the service

Run a simple Python client program to test that the model is being served. Note that the client code is specific to the model. If you serve a different model you will need to update the client program.

Install the Python client library on your machine.

```sh
pip install watson_nlp_runtime_client
```

Enable port forwarding from your local machine.

If running the service in a Kubernetes cluster:

```sh
kubectl port-forward svc/watson-nlp-runtime-service 8085
```

For OpenShift:

```sh
oc port-forward svc/watson-nlp-runtime-service 8085
```

Go to the directory with the client program and run it.

```sh
cd Client
```

Run the program with a single string argument.

```sh
python client.py "Watson NLP is awesome"
```

The program will return output similar to the following.

```sh
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
