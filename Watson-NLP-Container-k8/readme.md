# Serve Models on Kubernetes or OpenShift Using Standalone Containers
In this tutorial you will build a standalone container image to serve Watson NLP models, and then run it on a Kubernetes or OpenShift cluster. 

The standalone container image will include both the Watson NLP Runtime as well as models. When the container runs, it will expose gRPC and REST endpoints that clients can use to run inference against the served models.  

While this tutorial uses pretrained models, the approach can be adapted to serving custom models.

### Architecture diagram

![Diagram](Images/ReferenceArchitectureK8.png)

### Prerequisites
- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- You have a Kubernetes or OpenShift cluster on which you can deploy an application
- You have either the Kubernetes (`kubectl`) or OpenShift (`oc`) CLI installed, and configured to talk to your cluster.
- Your Kubernetes or OpenShift cluster has access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-labs/Watson-NLP/blob/main/access/README.md#kubernetes-and-openshift)
- [Watson NLP Runtime Python client library](https://github.com/ibm-build-labs/Watson-NLP/blob/main/access/README.md#python) is installed

## Steps

### 1. Clone the GitHub repository
Clone the repository containing the code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
### 2. Build the container image 
In this step, you will build a container image to deploy. If you already have a standalone container image to serve stock and/or custom Watson NLP models that you prefer to use, you can skip this step.

Go to the build directory.
```
cd Watson-NLP/Watson-NLP-Container-k8/Runtime
```
There is a Dockerfile in this directory. Run the build command.
```
docker build . -t watson-nlp-container:v1
```
This will create a Docker image called `watson-nlp-container:v1`.  When the container runs, it will serve two pretrained models: 
- `sentiment_document-cnn-workflow_en_stock` 
- `ensemble_classification-wf_en_emotion-stock`

### 3. Copy the image to a container registry
To deploy this image in Kubernetes or OpenShift cluster, you must first provision the image to a container repository that your cluster can access.  Tag your image with proper repository and namespace/project name. Replace `<REPO>` and `<PROJECT_NAME>` in the following commands based on your configuration.
```
docker tag watson-nlp-container:v1 <REPO>/<PROJECT_NAME>/watson-nlp-container:v1 
```
Push the image to upstream
```
docker push <REPO>/<PROJECT_NAME>/watson-nlp-container:v1 
```

### 3. Deploy in Kubernetes/OpenShift
Go here: 
```
cd deployment
```
In this directory is a Kubernetes manifest called `deployment.yaml` which can be used to deploy the model service. Before you start this service, you will need to update the image path in the `Deployment` to point to the registry you used.
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
            cpu: "500m" 
          limits: 
            memory: "4Gi" 
            cpu: "1000m" 
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

####  3.1 Run on Kubernetes
Run the below commands to deploy in the cluster from the directory `Watson-NLP/Watson-NLP-Container-k8`.
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
#### 3.2 Run on OpenShift

In openshift it is a privileged container. Create a service account and give the accout scc previllege to give extra permission to run the model.
```
oc create sa watson-nlp-sa
```

```
oc adm policy add-scc-to-user anyuid -z watson-nlp-sa
```

Run the below commands to deploy in the cluster from the project root directory `Watson-NLP/Watson-NLP-Container-k8`.
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
Finally, you can test the service using a simple Python client program. The client code is under the directory `Watson-NLP/Watson-NLP-Container-k8/Client`. Note that the client command is specific to the models. If you are using different models from the ones in the above build, you will have to change the client code.

Assuming that you start in the Runtime directory: 
```
cd ../Client 
```
Ensure that the Watson NLP Python SDK is installed on your machine. 
```
pip3 install watson_nlp_runtime_client 
```
Enable port forwarding from your local machine prior to running the test. For a Kubernetes cluster:
```
kubectl port-forward svc/watson-nlp-container 8085 
```
If you are using OpenShift:
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
