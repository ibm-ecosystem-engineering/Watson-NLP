## Serving Custom Models with a Standalone Container

In this tutorial, I am going to explain how to serve a custom fine tunned Watson NLP model by building a container image that contains both the Watson NLP Runtime together with the custom models. This container image can be deployed anywhere (Docker, Kubernetes, OpenShift) to serve the models. 
In addition, A Python client is developed for accessing the gRPC endpoint that is exposed by the Watson NLP Runtime to perform scoring on the running model.

## Resources:
GitHub Repo: https://github.com/ibm-build-labs/Watson-NLP/tree/main/Watson-NLP-Container
### Prerequisites
- Docker is installed on your workstation
- Python >= 3.9 installed in your workstation to run the client program
- An IBM Artifactory username and API key are required to build the Docker image. Set the following variables in your environment.
 -- ARTIFACTORY_USERNAME
 -- ARTIFACTORY_API_KEY

## Build and Run the Server
Clone the git repo 
```
git clone https://github.com/ibm-build-labs/Watson-NLP
```
```
cd Watson-NLP-Custom-Model-Container/Runtime
```

Here is a sample docker image, the base image is the Watson-nlp runtime. The base image includes three library, Watson_core, Watson_runtime and Watson_nlp. It is set as a build argument so that when you build a docker image you can pass the base image as an argument.

Place your custom models in the **models** directory, when you will build the image, model will be copied over to docker image.

```
ARG WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39"
FROM ${WATSON_RUNTIME_BASE} as base
ENV LOCAL_MODELS_DIR=/app/models
COPY models /app/models
```

When the container is started, it will serve the models and client program can make inference request for the served models over either a REST or gRPC interface.

#### Build
```
docker build . \
--build-arg WATSON_RUNTIME_BASE="wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com/watson-nlp-runtime:0.13.1_ubi8_py39" \
-t watson-nlp-custom-container:v1
```
#### Run

Use the following command to start the server on your local machine.
```
docker run -d -p 8085:8085 watson-nlp-custom-container:v1
```
### Test

We have a simple Python client program that you can use to test the service. You need to ensure that the Watson NLP Python SDK is installed on your machine
```
pip3 install watson_nlp_runtime_client
```
To make the call to the gRPC inference service, you need the followings
- Model id, it is passed as a header argument, mm-model-id : “<MODEL_ID>”. Name of the model is the exported model placed in models directory.
- Make a request object based. 
- Call the stub installed by Watson_nlp_runtime_client

Here is a sample code snippet
```
#emotion analysis ensemble_classification-wf_en_emotion-stock
def call_emotion_model(self, inputText):
    request = common_service_pb2.EmotionDocumentWorkflowRequest(
        raw_document=dm.RawDocument(text=inputText).to_proto()
    )
    EMOTION_CLASSIFICATION_STOCK_MODEL = os.getenv("EMOTION_CLASSIFICATION_STOCK_MODEL", default="ensemble_classification-wf_en_emotion-stock")
        
    response = self.stub.EmotionDocumentWorkflowPredict(request,metadata=[("mm-model-id", EMOTION_CLASSIFICATION_STOCK_MODEL)] )
    return response
```
Go the Client directory from project Watson-NLP-Custom-Model-Container and pass the input text as a parameter to get sentiment and emotion analysis.
```
cd ../Client
```
```
python3 client.py "Watson NLP is awesome"
```
