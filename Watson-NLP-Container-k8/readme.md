# Serving Models with Standalone Containers on Kubernetes and OpenShift
In this tutorial you will learn how to serve Watson NLP models using a standalone container on a Kubernetes or OpenShift cluster.  For the tutorial you will use stock models for Sentiment Analysis and Emotion Classification, though you can use the same approach to serve other stock models or custom models that you have trained on Kubernetes or OpenShift.

The standalone container image includes both the Watson NLP Runtime and the models to be served.  When the container runs, it exposes a gRPC and REST endpoints that clients can use to run inference against the served models.  The advantage of using standalone containers is that they can be deployed on any container runtime.

### Architecture diagram

![Diagram](Images/ReferenceArchitectureK8.png)

### Prerequisites
- Docker is installed on your workstation.
- Python >= 3.9 installed in your workstation.  (This is needed to run the client program.)
- An [IBM Artifactory](https://na.artifactory.swg-devops.com/ui/admin/artifactory/user_profile) user name and API key are required to build the Docker image. Get an Artifactory Api key from [here](https://taas.w3ibm.mybluemix.net/guides/create-apikey-in-artifactory.md)
  - ARTIFACTORY_USERNAME 
  - ARTIFACTORY_API_KEY
  
Set the following variables in your environment.
```
export ARTIFACTORY_USERNAME=<USER_NAME>
export ARTIFACTORY_API_KEY=<API_KEY>
```

## Steps

### 1. Clone the git repo
Clone the GitHub repository containing our example code. Go to the directory that contains the code used in this tutorial.

```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
Go to the project directory for this tutorial.
```
cd Watson-NLP/Watson-NLP-Container-k8
```
### 2. Build the container image 
If you already have a standalone container image that you have created to serve models, you can skip this step.

Go to the directory `Runtime`.
```
cd Runtime
```
This directory contains the Dockerfile we will use to build the standalone container image.
```
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39"
FROM ${WATSON_RUNTIME_BASE} as base
#################
## Build Phase ##
#################
FROM base as build

# Args for artifactory credentials
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_API_KEY
ENV ARTIFACTORY_USERNAME=${ARTIFACTORY_USERNAME}
ENV ARTIFACTORY_API_KEY=${ARTIFACTORY_API_KEY}

# Build arg to specify space-delimited names of models
ARG MODEL_NAMES
WORKDIR /app/models
# Download all of the models locally to /app/models
RUN true && \
    mkdir -p /app/models && \
    arr=(${MODEL_NAMES}) && \
    for model_name in "${arr[@]}"; do \
        python3 -c "import watson_nlp; watson_nlp.download('${model_name}', parent_dir='/app/models')"; \
    done && \
    true

###################
## Release Phase ##
###################
FROM base as release

ENV LOCAL_MODELS_DIR=/app/models
COPY --from=build /app/models /app/models
```

Observe that the build uses the Watson NLP Runtime container image as the base image. Stock models are downloaded to the build machine during the build phase, and then copied into the image during the release phase.

The four build arguments are used for this Dockerfile.  Set these as environment variables.  
- **WATSON_RUNTIME_BASE**=Watson base runtime image (optional).
- **ARTIFACTORY_USERNAME**=Artifactory username to download the base image
- **ARTIFACTORY_API_KEY**=Artifactory API key to download the base image
- **MODEL_NAMES**=Space-separated list of models to be served. 

To build a Docker image, run the following command.
```
docker build . \
--build-arg WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39" \
--build-arg MODEL_NAMES="ensemble_classification-wf_en_emotion-stock sentiment_document-cnn-workflow_en_stock" \
--build-arg ARTIFACTORY_API_KEY=$ARTIFACTORY_API_KEY \
--build-arg ARTIFACTORY_USERNAME=$ARTIFACTORY_USERNAME \
-t watson-nlp-container:v1
```

This will create a Docker image called `watson-nlp-container:v1`.  When the container runs, it will serve two stock models: 
- sentiment_document-cnn-workflow_en_stock 
- ensemble_classification-wf_en_emotion-stock 

### 3. Copy the image to a container registry
To use this image in Kubernetes or OpenShift cluster, you need to provision the image to a repository so that during deployment cluster can pull the image.  Tag your image with proper repository and namespace/project name. replacing the <REPO> and <PROJECT_NAME> based on your configuration.
```
docker tag watson-nlp-container:v1 <REPO>/<PROJECT_NAME>/watson-nlp-container:v1 
```
Push the image to upstream
```
docker push <REPO>/<PROJECT_NAME>/watson-nlp-container:v1 
```

### 3. Deploy in Kubernetes/OpenShift

To run the service in an OpenShift or Kubernetes cluster, ensure that you have access to the cluster and that you have either the Kubernetes CLI (kubectl) or OpenShift CLI (oc) installed on your local machine.  Further, ensure that the Docker image you created above is in a container registry that is accessible from your Kubernetes or OpenShift cluster. Login to your Kubernetes/OpenShift cluster.
 
Below is an example of the YAML file to use.  There are two Kubernetes resources in the file:  a Deployment and a Service. 
 
You will need to update the image path in the Deployment to point to the container registry where you have stored your container image. 
```
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: watson-nlp-container 
spec: 
  selector: 
    matchLabels: 
      app: watson-nlp-container 
  replicas: 1 
  template: 
    metadata: 
      labels: 
        app: watson-nlp-container 
    spec: 
      containers: 
      - name: watson-nlp-container 
        image: image-registry.openshift-image-registry.svc:5000/openshift/watson-nlp-container:v1 
        resources: 
          requests: 
            memory: "2Gi" 
            cpu: "1000m" 
          limits: 
            memory: "4Gi" 
            cpu: "2000m" 
        ports: 
        - containerPort: 8085 
--- 
apiVersion: v1 
kind: Service 
metadata: 
  name: watson-nlp-container 
spec: 
  type: ClusterIP 
  selector: 
    app: watson-nlp-container 
  ports: 
  - port: 8085 
    protocol: TCP 
    targetPort: 8085 
```
Run the below commands to deploy in the cluster from the project root directory Watson-NLP-C 
Container.
####  3.1 Kubernetes
Run the below commands to deploy in the cluster from the project root directory `Watson-NLP-Container-k8`.
```
kubectl apply -f Runtime/deployment/deployment.yaml 
```
Check that the pod and service are running. 
```
kubectl get pods
```
```
kubectl get svc
```
#### 3.2 OpenShift
Run the below commands to deploy in the cluster from the project root directory `Watson-NLP-Container-k8`.
```
oc apply -f Runtime/deployment/deployment.yaml 
```
Check that the pod and service are running. 
```
oc get pods 
```
```
oc get svc 
```


### 4. Test
We will test the service using a simple Python client program.  The client code is under the directory **Watson-NLP-Container-k8/Client**.  Assuming we start in the Runtime directory: 
```
cd ../Client 
```
Ensure that the Watson NLP Python SDK is installed on your machine. 
```
pip3 install watson_nlp_runtime_client 
```
Enable port forwarding from your local machine prior to running the test. 
**Kubernetes**
```
kubectl port-forward svc/watson-nlp-container 8085 
```
**OpenShift**
```
oc port-forward svc/watson-nlp-container 8085
```

The client command expects a single text string argument, and requests inference scoring of the models being served.  Run the client command as: 
```
python3 client.py "Watson NLP is awesome" 
```

##### Output

```
classes {
  class_name: "joy"
  confidence: 0.9687168002128601
}
classes {
  class_name: "anger"
  confidence: 0.03973544389009476
}
classes {
  class_name: "fear"
  confidence: 0.030667975544929504
}
classes {
  class_name: "sadness"
  confidence: 0.016257189214229584
}
classes {
  class_name: "disgust"
  confidence: 0.0033179237507283688
}
producer_id {
  name: "Voting based Ensemble"
  version: "0.0.1"
}

score: 0.9761080145835876
label: SENT_POSITIVE
sentiment_mentions {
  span {
    end: 21
    text: "Watson NLP is awesome"
  }
  score: 0.9761080145835876
  label: SENT_POSITIVE
}
producer_id {
  name: "Document CNN Sentiment"
  version: "0.0.1"
}
```