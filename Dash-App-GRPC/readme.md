## Watson NLP Python Client 
In this tutorial you will build and deploy a Watson NLP client application.  The sample client application is a web service built in Python that performs Sentiment Analysis and Emotion Classification on user-supplied texts.  The client application uses the Watson NLP Python SDK to interact with a back-end model service.

You can adapt the sample code from this tutorial to your own projects.

This tutorial follows on from previous tutorials serving Sentiment Analysis and Emotion Classification models.  As a starting point, you should have a running instance of the Watson NLP Runtime that is serving Sentiment Analysis and Emotion Classification models. 

### Architecture Diagram

![Reference architecure](images/referenceArchitecturePythonClient.png)

We will first build a container image for the application, and then run it with either Docker, or on a Kubernetes or OpenShift cluster. At the end of the tutorial, we will take a closer look at the application code.

### Prerequisites: 
- Docker is installed on your local machine. 
- Python >= 3.9 is installed on your local machine. 
- You have access to a running instance of the Watson NLP Runtime running Sentiment Analysis and Emotion Classification models. 

## Steps
### 1. Clone the GitHub repository
Clone the repository containing the sample code for this tutorial. 
```
git clone https://github.com/ibm-build-labs/Watson-NLP
```
Go to the root directory for this tutorial.
```
cd Watson-NLP/Dash-App-GRPC
```
### 2. Install library
Installing the Watson NLP Python SDK.  This is a packaged gRPC stub library that is used to communicate with the Watson NLP Runtime.  
```
pip3 install watson_nlp_runtime_client 
```
### 3. Build docker image
Th Docker file for the application. In the requirement.txt all the required package are listed.  
```
FROM python:3.9 
WORKDIR /app 
COPY requirements.txt /app/requirements.txt 
RUN pip3 install -r requirements.txt 
ENV GRPC_SERVER_URL "localhost:8085" 
ENV SYNTAX_IZUMO_EN_STOCK_MODEL "sentiment_document-cnn-workflow_en_stock" 
ENV SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL "sentiment_document-cnn-workflow_en_stock" 
ENV EMOTION_CLASSIFICATION_STOCK_MODEL "ensemble_classification-wf_en_emotion-stock" 
ENV NLP_MODEL_SERVICE_TYPE="mm-model-id" 
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION python 
EXPOSE 8050 
COPY ./*.py /app 
COPY ./assets /app/assets 
CMD ["python3","Sentiment_dash_app.py"] 
```
Make sure you are in the root directory of the project where the docker file resides before you execute the below command. 
```
docker build -t dash-app-grpc:latest . 
```

### 4. Run

#### 4.1 Running the app in localhost 

Run the below command to run the container.
```
docker run \ 
-e GRPC_SERVER_URL=${GRPC_SERVER_URL} \ 
-e SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL=${SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL} \ 
-e EMOTION_CLASSIFICATION_STOCK_MODEL=${EMOTION_CLASSIFICATION_STOCK_MODEL} \ 
-e NLP_MODEL_SERVICE_TYPE=${NLP_MODEL_SERVICE_TYPE} \ 
-p 8050:8050 dash-app-grpc:latest 
```

Pass the environment variable with proper values 
- GRPC_SERVER_URL: It is gRPC endpoint with port. The default value is “localhost:8085”. For OpenShift the value would be <Service Name>:<Port> 
- SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL: This is sentiment analysis stock model. Default value is “entiment-document-cnn-workflow-en-stock” 
- EMOTION_CLASSIFICATION_STOCK_MODEL: This is emotion analysis stock model. Default value is “ensemble-classification-wf-en-emotion-stock” 
- NLP_MODEL_SERVICE_TYPE: This is runtime deployment type. Default value is “mm-model-id”. For WML Serving runtime running in K8/Openshift please set value “mm-vmodel-id” 

You can now access the application at 
```
http://localhost:8050 
```

#### 4.2 Running the application in a Kubernetes and OpenShift cluster 
 
Before running the app in localhost, you need to push to image in a container registry. Please change the `<Image Registry> and <Project Name>` based on your configuration. 
```
docker tag dash-app-grpc:latest <Image Registry>/<Project Name>/dash-app-grpc:latest 
```
```
docker push <Image Registry>/<Project Name>/dash-app-grpc:latest 
```
All the deployment files are in the deployment directory. In deployment.yaml file you need to modify set the image location based on the image you built in the previous step. 

**Image:** `<Image Registry>/<Project Name>/dash-app-grpc:latest` 

There are three Kubernetes resource files in the deployment directory 
- config.yaml 
- deployment.yaml 
- service.yaml

**deployment.yaml**

Deployment object describes mainly the number of replicas and the image path. Image path needs to be changed based on where you put the image in your container registry. Change the Docker image repo in spec.containers.image in deployment.yaml file. All the environment variables are set using config map describes in config.yaml. 
```
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: dash-app-grpc 
spec: 
  selector: 
    matchLabels: 
      app: dash-app-grpc 
  replicas: 1 
  template: 
    metadata: 
      labels: 
        app: dash-app-grpc 
    spec: 
      containers: 
      - name: dash-app-grpc 
        image: image-registry.openshift-image-registry.svc:5000/openshift/dash-app-grpc:2022083111 
        env: 
          - name: EMOTION_CLASSIFICATION_STOCK_MODEL 
            valueFrom: 
              configMapKeyRef: 
                key: EMOTION_CLASSIFICATION_STOCK_MODEL 
                name: dahsapp-config 
          - name: GRPC_SERVER_URL 
            valueFrom: 
              configMapKeyRef: 
                key: GRPC_SERVER_URL 
                name: dahsapp-config 
          - name: SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL 
            valueFrom: 
              configMapKeyRef: 
                key: SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL 
                name: dahsapp-config 
          - name: SYNTAX_IZUMO_EN_STOCK_MODEL 
            valueFrom: 
              configMapKeyRef: 
                key: SYNTAX_IZUMO_EN_STOCK_MODEL 
                name: dahsapp-config 
          - name: NLP_MODEL_SERVICE_TYPE 
            valueFrom: 
              configMapKeyRef: 
                key: NLP_MODEL_SERVICE_TYPE 
                name: dahsapp-config 
        ports: 
        - containerPort: 8050 
```

**config.yaml:**

```
apiVersion: v1 
data: 
  EMOTION_CLASSIFICATION_STOCK_MODEL: ensemble-classification-wf-en-emotion-stock-predictor 
  GRPC_SERVER_URL: wml-serving:8033 
  SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL: sentiment-document-cnn-workflow-en-stock-predictor 
  SYNTAX_IZUMO_EN_STOCK_MODEL: syntax-izumo-en-stock-predictor 
  NLP_MODEL_SERVICE_TYPE: mm-vmodel-id 
kind: ConfigMap 
metadata: 
  name: dahsapp-config 
```

In the config.yaml file below environment variables need to be set. Please change according to your requirement. Make sure you set the GRPC_SERVER_URL correct. 

- **GRPC_SERVER_URL:** It is gRPC endpoint with port. For OpenShift the value would be <Service Name>:<Port> for example “wml-serving:8033” 
- **SENTIMENT_DOCUMENT_CNN_WORKFLOW_MODEL:** This is sentiment analysis stock model. Default value is “entiment-document-cnn-workflow-en-stock” 
- **EMOTION_CLASSIFICATION_STOCK_MODEL:** This is emotion analysis stock model. Default value is “ensemble-classification-wf-en-emotion-stock” 
- **NLP_MODEL_SERVICE_TYPE:** This is runtime deployment type. Default value is “mm-model-id”. For WML Serving runtime running in K8/Openshift please set value “mm-vmodel-id”

**service.yaml**

Service object describes to create a clusterIP service, so that we can expose the service outside later using port-forward. Port is exposed at 8050. 

```
apiVersion: v1 
kind: Service 
metadata: 
  name: dash-app-grpc 
spec: 
  type: ClusterIP 
  selector: 
    app: dash-app-grpc 
  ports: 
  - port: 8050 
    protocol: TCP 
    targetPort: 8050 
```
#### 4.2.1 OpenShift 

execute the below command to deploy in OpenShift Cluster.
```
oc apply -f deployment/ 
```
you can expose the service as a route, or you can do a port-forward to test the application as a route.
```
oc expose service/dash-app-grpc 
```
```
oc get route
```
or you can port forward the service to access in localhost 
```
oc port-forward svc/dash-app-grpc 8050 
```
#### 4.2.2 Kubernetes 
execute the below command to deploy in Kubernetes Cluster.
```
kubectl apply -f deployment/ 
```
port forward the service to access in localhost
```
kubectl port-forward svc/dash-app-grpc 8050 
```

You can now access the application at 
```
http://localhost:8050 
```


