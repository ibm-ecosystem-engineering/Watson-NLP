# Watson NLP Runtime in a Container
We are going to demonstrate how to build a Watson NLP Runtime container with some models. This container can be  deployed anywhere ( docker, k8, openshift)

There are two parts of this demonostration. The nlp runtime with preloaded model running in a container and then a simple python client is going to acess the gRPC endpoint exposed by the nlp runtime container.

## Prerequisites
- Docker is installed in your workstation
- Python >= 3.9 installed in your workstation to run the client program
- Artifactory user name and API key is required to build the Docker image. Set the following variables in your environment.
-- ARTIFACTORY_USERNAME
-- ARTIFACTORY_API_KEY

## Developing and running the server:
### 1. Building docker image
Go to the root directory of the project **Watson-NLP-Container** and run the below command. It will create a docker image **watson-nlp-container:v1**
```
docker build . \                                
  --build-arg MODEL_NAMES="ensemble_classification-wf_en_emotion-stock sentiment_document-cnn-workflow_en_stock" \
  --build-arg ARTIFACTORY_API_KEY=$ARTIFACTORY_API_KEY \
  --build-arg ARTIFACTORY_USERNAME=$ARTIFACTORY_USERNAME \
  -t watson-nlp-container:v1
```
### 1.1 Running watson nlp container in local workstation
```
docker run -p 8085:8085 watson-nlp-container:v1
```
The gRPC service will be exposed in localhost 8085

### 1.2 Running watson nlp container in OpenShift/K8 cluster
Make sure you have proper access to the cluster and following tools are installed in your workstation
- kubernetes cli or openshift oc cli

Assuming that the docker file you craeted in step 1 is accessible in your OpenShift/k8 cluster. Please change the docker image repo in the **Runtime/Deployment/deployment.yaml** file.
Run the below commands to deploy in the cluster from the project root directory **Watson-NLP-Container**
**In OpenShift**
```
oc apply -f Runtime/deployment/deployment.yaml
```
Check if the pod and service are running
```
oc get pods
oc get svc
```
**In k8**
```
kubectl apply -f Runtime/deployment/deployment.yaml
```
Check if the pod and service are running
```
kubectl get pods
kubectl get svc
```
## 2 Testing the Watson NLP Runtime with a python client
To run this application you need to gain access to Artifactory to install the below client library
- **watson_nlp**: Data model is going to be used to prepare the request object
- **watson_nlp_runtime_client:** it is a packaged gRPC stub libary to communicate to the watson nlp runtime

Steps to create the client application
**Install python library**
 ``` 
pip install watson_nlp
pip install watson_nlp_runtime_client
```

- Create a gRPC channel
- Creat a request object
- Call the model by passing model id

A sample code can be found in [GrpcClient](GrpcClient.py)

As discussed erlier there are two versions of Watson NLP runtime are running
- In local docker container
- And in k8/OpenShift cluster

### 2.1 Run against local docker container
Go the Client directory from project Watson-NLP-Container
```
cd Client
python3 client.py
```
### 2.2 Run against OpenShift/k8 cluster
First do a port forwarding to access the Watson NLP Runtime
In openshift
```
oc port-forward svc/watson-nlp-container 8085
```
In kubernetes
```
kubectl port-forward svc/watson-nlp-container 8085
```
```
cd Client
python3 client.py
```