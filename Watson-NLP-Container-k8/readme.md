# Watson NLP Runtime in a Container
In this directory, we will learn how to serve pre-trained Watson NLP models from a standalone container.  For the examples, we will use stock models for Sentiment Analysis and Emotion Classification.

By standalone container, we mean that the container image is self-contained and includes both ML models and the model runtime.  When the container runs it exposes REST and gRPC endpoints that a client program can use to run scoring against the models.  

Standalone containers are useful since they can be deployed in a variety of contexts.  In this tutorial, we will deploy on a Kubernetes or OpenShift cluster.

In addition to serving the models, this tutorial demonstrates how to testing the service by running a simple Python client program. 

### Architecture diagram

![Diagram](Images/ReferenceArchitectureK8.png)

### Prerequisites
- Docker is installed on your workstation
- Python >= 3.9 installed in your workstation to run the client program
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
Clone the git repository containing our example code. Go to the directory that contains the code used in this tutorial.

```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
Go to the project directory for this tutorials
```
cd Watson-NLP/Watson-NLP-Container-Local
```
### 2. Build
Go to the directory `Runtime`
```
cd Runtime
```
We will build the container image for the service with the following Dockerfile. 
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

For the build we use the Watson NLP Runtime container image as the base image. Stock models are downloaded to the build machine during the build phase, and then copied into the image during the release phase.

Below are the four build arguments that needto be passed during building the image,
- **WATSON_RUNTIME_BASE**=Watson base runtime image. you may provide any version you want. the default version is 13.1
- **ARTIFACTORY_USERNAME**=Artifactory username to download the base image
- **ARTIFACTORY_API_KEY**=Artifactory API key to download the base image
- **MODEL_NAMES**=argument is the ML model you want to include in the container. You can pass multiple model names with space separated.

**LOCAL_MODELS_DIR** is the directory from where Watson runtime reads all the models. You don’t have to change anything here.Finally copy all the model from the base stage to release stage.To build a docker image, run the following command. 

Finally copy all the model from the base stage to release stage. 
 
To build a docker image, run the following command.
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

To use this image in kubernetes/OpenShift cluster, you need an image repository so that during deployment cluster can pull the image. In this example I am using IBM cloud container registry. You can choose a repository on your own.

Tag your image with proper repository and namespace/project name. replacing the <REPO> and <PROJECT_NAME> based on your configuration.
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
