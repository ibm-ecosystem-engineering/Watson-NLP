# Serve Pretrained Models on Kubernetes or OpenShift
In this tutorial you will serve Watson NLP pretrained models on a Kubernetes or OpenShift cluster. 

You will create a Kubernetes Deployment to run the Watson NLP Runtime image. In the Pods of this Deployment, pretrained model images are specified as *init containers*. These init containers will run to completion before the main application starts, and will provision models to the *emptyDir* volume of the Pod. When the Watson NLP Runtime container starts it will load the models and begin serving them.

When using this approach, models are kept in separate containers from the runtime. To change the set of served models you need only to update the Kubernetes manifest. 

### Prerequisites
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- You have a Kubernetes or OpenShift cluster on which you can deploy an application
- You have either the Kubernetes (`kubectl`) or OpenShift (`oc`) CLI installed, and configured to talk to your cluster.
- Your Kubernetes or OpenShift cluster has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/access/README.md#kubernetes-and-openshift)
- [Watson NLP Runtime Python client library](https://github.com/ibm-build-labs/Watson-NLP/blob/main/access/README.md#python) is installed

**Tip**:
- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.

## Steps

### 1. Get the sample code
Clone the GitHub repository containing the sample code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
Go to the directory with code used in this tutorial.
```
cd Watson-NLP/Init-Container
```

### 2. Deploy the service
If using Kubernetes:
```
kubectl apply -f deployment/deployment.yaml
```
If using OpenShift:
```
oc apply -f deployment/deployment.yaml
```
The model service is now deployed.  

### 3. Test the service
Run a simple Python client program to test that the model is being served. Note that the client code is specific to the model. If you serve a different model you will need to update the client program.

Ensure that the Watson NLP Python SDK is installed on your machine. 
```
pip3 install watson_nlp_runtime_client 
```
Enable port forwarding from your local machine. For a Kubernetes cluster:
```
kubectl port-forward svc/watson-nlp-container 8085 
```
If you are using OpenShift:
```
oc port-forward svc/watson-nlp-container 8085
```
Go to the directory with the client program and run it.   
```
cd client
```
```
python3 client.py "Watson NLP is awesome" 
```
The client command expects a single text string argument. The client will print out the inference response returned by the model.

## Understanding the Kubernetes Manifest

Examine the Kubernetes manifest used to deploy the model service.  
```
cat deployment/deployment.yaml
```
This manifest consists of a Kubernetes Deployment and a Service. The Pods of the Deployment will all serve the same set of models. The Service provides an endpoint for the service, and load balancing.

Observe that the Pods of the Deployment have an init container specified, which use the container image of a Watson NLP pretrained model. 
```
      initContainers:
      - name: initial-model-loading-emotion-classification
        image: image-registry.openshift-image-registry.svc:5000/poc/watson-nlp_classification_ensemble-workflow_lang_en_tone-stock:2.3.1
        volumeMounts:
        - name: model-directory
          mountPath: "/app/models"       
```
The init containers of a Pod will run to completion before the main application container starts. These containers will provision the models so that the Watson NLP Runtime can find them. You can change the image name to serve other pretrained models. As well, you can serve multiple models at once by specifying multiple init containers.

The model container mounts the Pod's `emptyDir` volume at path `/app/models`. The entrypoint script for the model container will copy the model to this location when it runs.

The main application container image is the Watson NLP Runtime.
```
      containers:
      - name: watson-main-container
        image: image-registry.openshift-image-registry.svc:5000/poc/runtime:13.1.0
        env:
        - name: LOCAL_MODELS_DIR
          value: "/app/models"
        - name: LOG_LEVEL
          value: debug
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        ports:
        - containerPort: 8080
        - containerPort: 8085
        volumeMounts:
        - name: model-directory
          mountPath: "/app/models"
```
Note that this container also mounts the Pod's `emptyDir` volume at path `/app/models`. The environment variable `LOCAL_MODELS_DIR` is set to `/app/models` to inform the Watson NLP Runtime where to find the models.
