# Serve Watson MLP Models Using Knative Serving

With IBM Watson NLP, IBM introduced a common library for natural language processing, document understanding, translation, and trust. IBM Watson NLP brings everything under one umbrella for consistency and ease of development and deployment. This tutorial shows you how to build a standalone container image to serve Watson NLP models, and then run it using **Knative Serving** in an Openshift cluster.

**Knative Serving** is an Open-Source Enterprise-level solution to build Serverless and Event Driven Applications in Kubernetes / Openshift cluster. For more information see [https://knative.dev/docs/](https://knative.dev/docs/).

A standalone container image includes both the Watson NLP Runtime as well as the models to be served. When the container runs, it exposes gRPC and REST endpoints that clients can use to run inference on the served models.

This tutorial uses pretrained models, however the approach can be adapted to serving custom models.

## Prerequisites

To follow this tutorial, you need:

- [Docker Desktop](https://docs.docker.com/get-docker/) installed.
- [Python 3.9](https://www.python.org/downloads/) or later installed.
- A Red Hat OpenShift cluster on which you can deploy an application. For this tutorial, you can reserve an [OpenShift Sandbox](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/reserve-openshift-sandbox).
- Red Hat OpenShift CLI (```oc```) installed, and configured to talk to your cluster.
- Your Kubernetes or Red Hat OpenShift cluster must be able to access Watson NLP Runtime and pretrained models. Follow the directions [here](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift).
- The [Watson NLP Runtime Python client library installed](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#python)

**Tip:** Podman provides a Docker-compatible command-line front end. Unless otherwise noted, all of the Docker commands in this tutorial should work for Podman if you alias the Docker CLI with the shell command:

```bash
alias docker=podman
```

## Steps

### Step 1. Install Knative

In this tutorial we are using OpenShift Serverless Operator for knative serving. There are two step processs to install knative serving

- [Install the OpenShift Serverless Operator](https://docs.openshift.com/container-platform/4.10/serverless/install/install-serverless-operator.html)
- [Install Knative Serving](https://docs.openshift.com/container-platform/4.10/serverless/install/installing-knative-serving.html)
- Optional. The Knative CLI client kn can be used to simplify the deployment. [Install the Knative CLI](https://knative.dev/docs/client/install-kn/)

### Step 2. Clone the GitHub repository

Clone the repository that contains the code used in this tutorial.

```sh
git clone https://github.com/ibm-build-labs/Watson-NLP
```

### Step 3. Build the container image

Build a container image to deploy. If you already have a stand-alone container image to serve pretrained or custom Watson NLP models that you prefer to use, you can skip this step.

Go to the build directory.

```sh
cd Watson-NLP/MLOps/Watson-NLP-Knative/runtime
```

There should be a Dockerfile in this directory. Run the build command.

```sh
docker build . -t watson-nlp-container:v1
```

This creates a Docker image called watson-nlp-container:v1. When the container runs, it will serve 2 pretrained models:

- sentiment_document-cnn-workflow_en_stock
- ensemble_classification-wf_en_emotion-stock

### Step 4. Copy the image to a container registry

To deploy this image in Kubernetes or Red Hat OpenShift cluster, you must first provision the image to a container repository that your cluster can access. Tag your image with proper repository and namespace/project names. Replace ***<REGISTRY>*** and ***<NAMESPACE>*** in the following commands based on your configuration.

**Note:** If you reserved a sandbox in the IBM TechZone, you will find ***<REGISTRY>*** and ***<NAMESPACE>*** in the confirmation email that you received when the sandbox was ready. See the following image.

***REGISTRY*** = Integrated OpenShift container image registry: you received in the email
  
***NAMESPACE*** = Project name: you received in the email

![Reference architecure](images/techzoneemail.png)

```sh
docker tag watson-nlp-container:v1 <REGISTRY>/<NAMESPACE>/watson-nlp-container:v1
```

Push the image to upstream.

```sh
docker push <REGISTRY>/<NAMESPACE>/watson-nlp-container:v1
```

### Step 5. Deploying the app in Red Hat OpenShift Knative serving

After the building the docker image and pushed to registry, you can deploy the app into your cluster.

During the creation of a Service, Knative performs the following steps:

- Create a new immutable revision for this version of the app.
- Network programming to create a Route, ingress, Service, and load balancer for your app.
- Automatically scale your pods up and down, including scaling down to zero active pods.

We can deploy the model in Knative serverless in two ways
  
- using knative commandline tool `kn`
- standard Kubernetes manifest

I am going to show the both type of deployment. You may choose any of the method.
  
To start, lets create a new project in OpenShift Cluster

```sh
oc new-project knative-demo
```

#### 5.1 Deploy using Knative cli tool

Make sure you have installed Knative [cli tool](https://knative.dev/docs/client/install-kn/).
In this deployment, we are using the image us.icr.io/watson-core-demo/watson-nlp-container:v1, is hosted in the IBM Container Registry. Please replace the image url in the command below to the one you built.

##### Create a knative service

```sh
kn service create watson-nlp-kn \
  --image us.icr.io/watson-core-demo/watson-nlp-container:v1 \
  --env ACCEPT_LICENSE=true \
  --env LOG_LEVEL=debug
```

you should see a log message like below

```
Creating service 'watson-nlp-kn' in namespace 'knative-demo':

  0.211s The Route is still working to reflect the latest desired specification.
  0.221s ...
  0.265s Configuration "watson-nlp-kn" is waiting for a Revision to become ready.
 81.742s ...
 81.812s Ingress has not yet been reconciled.
 82.037s Waiting for load balancer to be ready
 82.218s Ready to serve.

Service 'watson-nlp-kn' created to latest revision 'watson-nlp-kn-00001' is available at URL:
```

##### Check if the serivce is working

```sh
kn service list
```

###### check the revision

```
kn revision list
```

output:

```
NAME                  SERVICE         TRAFFIC   TAGS   GENERATION   AGE     CONDITIONS   READY   REASON
watson-nlp-kn-00001   watson-nlp-kn   100%             1            2m43s   3 OK / 4     True 
```

##### Find the domain url for your service

```sh
kn service describe watson-nlp-kn -o url
```

Set the service url in a varaible for testing in the next section
  
```sh
export SERVICE_URL=$(kn service describe watson-nlp-kn -o url)
```

#### 5.2 Deploy using Kubernetes manifest

Go to the deployment directory.

```sh
cd deployment
```

In the directory, you should find a Kubernetes manifest called deployment.yaml which can be used to deploy the model service. The default image in this deployment, us.icr.io/watson-core-demo/watson-nlp-container:v1, is hosted in the IBM Container Registry. Before you start this service, you must update the image path in the Deployment to point to the registry you used.

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: watson-nlp-kn
spec:
  template:
    metadata:
    spec:
      containers:
      - name: watson-nlp-runtime
        image: us.icr.io/watson-core-demo/watson-nlp-container:v1
        env:
        - name: ACCEPT_LICENSE
          value: 'true'
        - name: LOG_LEVEL
          value: debug
        ports:
        - containerPort: 8080
```
  
Note: Ensure that the container image value in service.yaml matches the container you built in the previous step.

  ```sh
  oc apply -f knative-service.yaml
  ```

##### Check if the service is up and running
  
  ```sh
  oc get configuration  
  ```
  
  Output:
  
  ```sh
  NAME            LATESTCREATED         LATESTREADY           READY   REASON
  watson-nlp-kn   watson-nlp-kn-00001   watson-nlp-kn-00001   True    

  ```
  
  check revision
  
  ```sh
  oc get revisions
  
  ```
  
##### Get the service url

  ```sh
  export SERVICE_URL=$(oc get ksvc watson-nlp-kn  -o jsonpath="{.status.url}")
  ```
  
### Step 6. Testing Knative autoscaling
  
With Knative autoscaling, code runs when it needs to, with Knative starting and stopping instances automatically. When there is no traffic no instance will be running of the app
  
lets Check currently running pods

  ```sh
  oc get pods
  ```

There should not see any pod runnng. If you see the 'watson-nlp-kn' is running wait for a minute and the instance should be terminated automatically.
  
#### Observe the pod status changing

  Open a new terminal to exceute the below command to watch pod status changing 
  ```sh
  oc get pods -w
  ```
  
  In the current terminal run the below commands to put some traffice in the service, 
  
  ```sh
  curl ${SERVICE_URL}
  ```
  
  ```sh
  NAME                                             READY   STATUS    RESTARTS   AGE
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     Pending   0          0s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     Pending   0          0s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     ContainerCreating   0          0s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     ContainerCreating   0          1s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     ContainerCreating   0          1s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   1/2     Running             0          2s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   2/2     Running             0          30s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   2/2     Terminating         0          90s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   1/2     Terminating         0          110s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   1/2     Terminating         0          2m1s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     Terminating         0          2m1s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     Terminating         0          2m1s
  watson-nlp-kn-00001-deployment-6966f5cc9-pfkrc   0/2     Terminating         0          2m1s
  ```
  
  if you observe the status of the pod, when you put some traffic pod started to wake up and then after a while it got terminated.
  
### Step 7. Testing ML Model serving

  #### Calling the `ensemble_classification-wf_en_emotion-stock` model
 
  ```sh
    curl -X POST "${SERVICE_URL}/v1/watson.runtime.nlp.v1/NlpService/ClassificationPredict" -H "accept: application/json" -H "grpc-metadata-mm-model-id: classification_ensemble-workflow_lang_en_tone-stock" -H "content-type: application/json" -d "{ \"rawDocument\": { \"text\": \"Watson nlp is awesome! works in knative\" }}"
  ```
  #### Calling the `sentiment_document-cnn-workflow_en_stock` model
  
  ```
  curl -X POST "${SERVICE_URL}/v1/watson.runtime.nlp.v1/NlpService/SentimentPredict" -H "accept: application/json" -H "grpc-metadata-mm-model-id: sentiment_aggregated-cnn-workflow_lang_en_stock" -H "content-type: application/json" -d "{ \"rawDocument\": { \"text\": \"Watson nlp is awesome! works in knative\" }, \"languageCode\": \"en\", \"documentSentiment\": true, \"targetPhrases\": [ \"string\" ], \"showNeutralScores\": true}"
  ```
  
  
### Step 8. Deleting the app

  ```sh
  kn service delete watson-nlp-kn

  ```

  ```sh
  oc delete -f knative-service.yaml
  ```
