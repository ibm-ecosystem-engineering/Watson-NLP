# Watson NLP Python Client

In this tutorial you will build and deploy a Watson NLP client application. The sample client application is a web service built in Python that performs Emotion Classification on user-supplied texts. The client application uses the Watson NLP Python SDK to interact with a back-end model service. You can adapt the sample code from this tutorial to your own projects.

This tutorial follows from previous tutorials serving Emotion Classification models. You should have a model service that is serving Watson NLP Classification models. The default configuration uses the model:

- `classification_ensemble-workflow_lang_en_tone-stock`

## Architecture Diagram

![Reference architecure](images/referenceArchitecturePythonClient.png)

## Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) is installed
- [Python 3.9](https://www.python.org/downloads/) or later is installed
- [Watson NLP Runtime Python client library](https://github.com/ibm-ecosystem-engineering/Watson-NLP/blob/main/MLOps/access/README.md#python) is installed

**Tip**:

- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.

## Steps

### 1. Clone the GitHub repository

Clone the repository that contains the sample code used in this tutorial.

```sh
git clone https://github.com/ibm-ecosystem-engineering/Watson-NLP
```

Go to the root directory for this tutorial.

```sh
cd Watson-NLP/MLOps/Dash-App-GRPC
```

### 2. Install the client library

Run the following command to install the Watson NLP Python client library.

```sh
pip3 install watson_nlp_runtime_client
```

This is a packaged gRPC stub library that is used to communicate with the Watson NLP Runtime.

### 3. Build docker image

There is a `Dockerfile` in the root directory for this tutorial. Build the container image with the following command.

```sh
docker build -t dash-app-grpc:latest .
```

This results in an image named `dash-app-grpc:latest`.

### 4. Run with Docker

In this section, we give the steps to run your application front-end locally using Docker. If you instead want to run it on your Kubernetes or OpenShift cluster, skip ahead to the next step.

#### 4.1 Enable port forwarding

If your model service is running on a Kubernetes or OpenShift cluster, then enable port forwarding from your local machine to that cluster. If this is not the case, then skip this step.

In Kubernetes:

```sh
kubectl port-forward svc/watson-nlp-container 8085
```

For OpenShift:

```sh
oc port-forward svc/watson-nlp-container 8085
```

#### 4.2 Start the web service

Set the following environment variables:

- `GRPC_SERVER_URL`: Set this to the gRPC endpoint model service. The default value is `localhost:8085`.
- `TONE_CLASSIFICATION_STOCK_MODEL`: Set this to the name of the tone classification model being served. Default value is `classification_ensemble-workflow_lang_en_tone-stock`.
- `NLP_MODEL_SERVICE_TYPE`: This argument indicates the type of model serving platform. If you model is running in kubernetes as a container set the value as `mm-model-id`. If your model is running in a kserve/wml serving set the value as 'mm-vmodel-id'

Run this command to start the web service.

```sh
docker run \
-e GRPC_SERVER_URL=${GRPC_SERVER_URL} \
-e TONE_CLASSIFICATION_STOCK_MODEL=${TONE_CLASSIFICATION_STOCK_MODEL} \
-e NLP_MODEL_SERVICE_TYPE='mm-model-id' \
-p 8050:8050 dash-app-grpc:latest
```

#### 4.3 Test

Use your browser to access the application at the following URL.

```url
http://localhost:8050
```

### 5. Run the application in your Kubernetes or OpenShift cluster

In this section we discuss the steps to run the application on the same Kubernetes or OpenShift cluster in which your models are being served.

#### 5.1 Push the image to a container registry

First you will need to push the image to a container registry that can be accessed by your cluster. Run the following commands, changing the `<Image Registry>` and `<Project Name>` in the following commands based on your configuration.

```sh
docker tag dash-app-grpc:latest <Image Registry>/<Project Name>/dash-app-grpc:latest
docker push <Image Registry>/<Project Name>/dash-app-grpc:latest
```

#### 5.2 Update the manifest

Starting at the root directory for this tutorial, go to the directory with the Kubernetes manifest.

```sh
cd deployment
```

There are three files in the directory.

- `config.yaml`
- `deployment.yaml`
- `service.yaml`

In `deployment.yaml` update the image line to point to the image that you pushed to a registry, i.e. change this line:

```yaml
       image: image-registry.openshift-image-registry.svc:5000/openshift/dash-app-grpc:2022083111
```

The format should be:

```yaml
       image: <Image Registry>/<Project Name>/dash-app-grpc:latest`
```

#### 5.3 Set environment variables

Set the following variables in your environment.

- `GRPC_SERVER_URL`: Set this to the gRPC endpoint of the model service. The value should have the form `<Service-Name>:<Port>`, e.g. `wml-serving:8033`.
- `TONE_CLASSIFICATION_STOCK_MODEL`: Set this to the name of the tone classification model being served. Default value is `classification_ensemble-workflow_lang_en_tone-stock`.
- `NLP_MODEL_SERVICE_TYPE`: This argument indicates the type of model serving platform. If you model is running in kubernetes as a container set the value as `mm-model-id`. If your model is running in a kserve/wml serving set the value as 'mm-vmodel-id'

#### 5.3 Deploy

**Kubernetes.** Execute the following command to deploy.

```sh
kubectl apply -f deployment/
```

Enable port-forward to the service in order to access it from your local machine.

```sh
kubectl port-forward svc/dash-app-grpc 8050
```

**OpenShift.** Execute the below command to deploy.

```sh
oc apply -f deployment/
```

You can expose the service as a route, or you can do a port-forward to test the application as a route.

```sh
oc expose service/dash-app-grpc
oc get route
```

Alternatively, you can port forward the service to access in localhost

```sh
oc port-forward svc/dash-app-grpc 8050
```

#### 5.4 Test

You can now access the application from your browser at the following URL.

```url
http://localhost:8050
```

## Understanding the Application Code

This application is built on python library `watson-nlp-runtime-client`. It is a gRPC client library contains all the generated python code to make inference call.

To implement this application the below libraries are needed.

```python
dash
dash_bootstrap_components
dash_daq
pandas
plotly
numpy
grpcio
protobuf==4.21.7
watson-nlp-runtime-client
```

`GrpcClient.py` is making the gRPC call to the inference service using `watson-nlp-runtime-client` library

```python
from watson_nlp_runtime_client import (
    common_service_pb2,
    common_service_pb2_grpc,
    syntax_types_pb2,
)
```

First it creates a gRPC channel and then using the channel object it creates the client stub to communicate to the server.

```python
GRPC_SERVER_URL = os.getenv("GRPC_SERVER_URL", default="localhost:8085")
channel = grpc.insecure_channel(GRPC_SERVER_URL)
self.stub = common_service_pb2_grpc.NlpServiceStub(channel)
```

The client stub accepts two parameters, a request object and header parameter

```python
def call_tone_model(self, inputText):
    request = common_service_pb2.SentimentRequest(
        raw_document=syntax_types_pb2.RawDocument(text=inputText)
    )
    TONE_CLASSIFICATION_STOCK_MODEL = os.getenv(
        "TONE_CLASSIFICATION_STOCK_MODEL",
        default="classification_ensemble-workflow_lang_en_tone-stock",
    )
    response = self.stub.ClassificationPredict(
        request,
        metadata=[(self.NLP_MODEL_SERVICE_TYPE, TONE_CLASSIFICATION_STOCK_MODEL)],
    )
    return response
```

`Tone_dash_app.py` uses python 'dash' library to display its graphs and user interface.
