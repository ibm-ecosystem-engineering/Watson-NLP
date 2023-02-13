# Serve Watson NLP Models with Google Cloud Run

[Google Cloud Run](https://cloud.google.com/run) is a managed compute platform that lets you run containers directly on top of Google's scalable infrastructure. You can deploy code written in any programming language on Cloud Run if you can build a container image from it. In fact, building container images is optional. Cloud Run allows developers to spend their time writing their code, and very little time operating, configuring, and scaling their Cloud Run service. Cloud Run also works well with other services on Google Cloud, so you can build full-featured applications.

This tutorial will walk you through the steps to deploy a standalone Watson NLP Runtime to Google Cloud Run.

## Prerequisites

- Your entitlement key to access the IBM Entitled Registry
- Access to a project in Google Cloud
- [Permissions](https://cloud.google.com/run/docs/securing/managing-access) to deploy containerized application to Cloud Run (roles/editor is sufficient)
- [Permissions](https://cloud.google.com/run/docs/authenticating/public) to grant unauthenticated users to the exposed REST service endpoint (roles/owner is sufficient)
- If you don't use Cloud Shell, make sure you have the following tools installed on your local machine:
  - [Docker](https://docs.docker.com/get-docker/)
  - [gcloud CLI](https://cloud.google.com/cli)
  - [grpcurl](https://github.com/fullstorydev/grpcurl/releases)

**Tip**:

- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.

## Create the runtime container image

The IBM Entitled Registry contains various container images for Watson Runtime. Once you've obtained the entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary), you can login to the registry with the key, and pull the runtime images to your local machine. The Watson Runtime on its own doesn't have any models included. However, you can easily build a runtime container image to include one or more pretrained models, which are also stored as container images in the IBM Entitled Registry.

### Step 1: Launch Google Cloud Shell

[Cloud Shell](https://cloud.google.com/shell) is an interactive shell environment for Google Cloud that lets you learn and experiment with Google Cloud and manage your projects and resources from your web browser. With Cloud Shell, the Google Cloud CLI and other utilities you need are pre-installed, fully authenticated, up-to-date, and always available when you need them. You can also install additional packages and tools you need into the Cloud Shell environment.

If you have access to multiple Google Cloud projects, make sure the environment variable `GOOGLE_CLOUD_PROJECT` in Cloud Shell is set to the correct project. You can use the `gcloud config set project` command to switch project if necessary.

### Step 2: Login to the IBM Entitled Registry

```sh
echo $IBM_ENTITLEMENT_KEY | docker login -u cp --password-stdin cp.icr.io/cp/ai
```

### Step 3: Download a couple of models to a local directory

Create a directory named `models`:

```sh
mkdir models && chmod 777 models
```

Set variable `REGISTRY` as follows to pull the images from IBM Entitled Registry:

```sh
REGISTRY=cp.icr.io/cp/ai
```

Use a variable `MODELS` to provide the list of models you want to download:

```sh
MODELS="watson-nlp_syntax_izumo_lang_en_stock:1.0.9 watson-nlp_syntax_izumo_lang_fr_stock:1.0.9"
```

Download the models into the local directory `models`:

```sh
for i in $(echo "$MODELS")
do
  image=${REGISTRY}/$i
  docker run -it --rm -e ACCEPT_LICENSE=true -v `pwd`/models:/app/models $image
done
```

### Step 4: Create a `Dockerfile` using a text editor of your choice

```dockerfile
ARG REGISTRY
ARG TAG=1.1.0
FROM ${REGISTRY}/watson-nlp-runtime:${TAG}
COPY models /app/models
USER root
RUN chmod a+r /tini
USER app
```

### Step 5: Build the runtime image

```sh
docker build . -t my-watson-nlp-runtime:latest --build-arg REGISTRY=${REGISTRY}
```

### Step 6: Upload your runtime image to Google Cloud Container Registry

Now the runtime image is created, let's put it on [Google Cloud Container Registry](https://cloud.google.com/container-registry), so that it can be used for deployment.

Tag the image:

```sh
docker tag my-watson-nlp-runtime:latest gcr.io/${GOOGLE_CLOUD_PROJECT}/my-watson-nlp-runtime:latest
```

Push the image:

```sh
docker push gcr.io/${GOOGLE_CLOUD_PROJECT}/my-watson-nlp-runtime:latest
```

List the images in Container Registry:

```sh
gcloud container images list
```

## Deploy the runtime to Cloud Run

Once the runtime image is uploaded to Container Registry, we can use it to deploy a Cloud Run service to serve Watson NLP models via either gRPC API or REST API.

### Step 7: Deploy a gRPC Service

```sh
gcloud run deploy my-watson-nlp-runtime-grpc \
--image=gcr.io/${GOOGLE_CLOUD_PROJECT}/my-watson-nlp-runtime:latest \
--set-env-vars=ACCEPT_LICENSE=true \
--memory=8Gi \
--cpu=4 \
--cpu-throttling \
--port=8085 \
--use-http2 \
--allow-unauthenticated \
--min-instances=0 \
--max-instances=3 \
--region=us-central1 \
--project=${GOOGLE_CLOUD_PROJECT}
```

### Step 8: Deploy a REST Service

```sh
gcloud run deploy my-watson-nlp-runtime-rest \
--image=gcr.io/${GOOGLE_CLOUD_PROJECT}/my-watson-nlp-runtime:latest \
--set-env-vars=ACCEPT_LICENSE=true \
--memory=8Gi \
--cpu=4 \
--cpu-throttling \
--port=8080 \
--allow-unauthenticated \
--min-instances=0 \
--max-instances=3 \
--region=us-central1 \
--project=${GOOGLE_CLOUD_PROJECT}
```

### Step 9: Check the deployed services

You can check the status of the services with the following commands.

List the services:

```sh
gcloud run services list
```

Check the logs:

```sh
gcloud beta run services logs tail <service>
```


## Access the API Services

### Step 10: Use curl to make a gRPC call

Once the gRPC service is ready, you should be able to send an inference request to the gRPC service endpoint using a `grpcurl` command.

You can extract the proto files of the gRPC from the runtime image as follows:

```sh
docker run -d --rm --name watson-nlp-runtime \
  -e ACCEPT_LICENSE=true \
  cp.icr.io/cp/ai/watson-nlp-runtime:1.1.0 sleep 100
docker cp watson-nlp-runtime:/app/protos .
```

Make a gRPC API call:

```sh
cd protos
grpcurl -proto common-service.proto \
  -H "mm-model-id: syntax_izumo_lang_en_stock" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ] }" \
  ${PUBLIC_ENDPOINT} watson.runtime.nlp.v1.NlpService.SyntaxPredict \
  | jq -r .
```

**Tip**:

- The metadata value for `mm-model-id` should match the folder name of the model when it was downloaded and saved in `./models` in Step 3.
- The ${PUBLIC_ENDPOINT} value can be found with command `gcloud run services describe my-watson-nlp-runtime-grpc --region=us-central1`, and should be specified in the `grpcurl` command as `<hostname>:443`, as opposed to `https://<hostname>`.

If you get a response like the following, the gRPC service is working properly.

```json
{
  "text": "This is a test.",
  "producerId": {
    "name": "Izumo Text Processing",
    "version": "0.0.1"
  },
  "tokens": [
    {
      "span": {
        "end": 4,
        "text": "This"
      }
    },
    {
      "span": {
        "begin": 5,
        "end": 7,
        "text": "is"
      }
    },
    {
      "span": {
        "begin": 8,
        "end": 9,
        "text": "a"
      }
    },
    {
      "span": {
        "begin": 10,
        "end": 14,
        "text": "test"
      }
    },
    {
      "span": {
        "begin": 14,
        "end": 15,
        "text": "."
      }
    }
  ],
  "sentences": [
    {
      "span": {
        "end": 15,
        "text": "This is a test."
      }
    }
  ],
  "paragraphs": [
    {
      "span": {
        "end": 15,
        "text": "This is a test."
      }
    }
  ]
}
```

### Step 11: Use curl to make a REST call

Once the REST service is ready, you should be able to send an inference request to the REST service endpoint using a `curl` command.

Make a REST API call:

```sh
curl -s -X POST "${PUBLIC_ENDPOINT}/v1/watson.runtime.nlp.v1/NlpService/SyntaxPredict" \
  -H "accept: application/json" \
  -H "grpc-metadata-mm-model-id: syntax_izumo_lang_en_stock" \
  -H "content-type: application/json" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ] }" \
  | jq -r .
```

**Tip**:

- The metadata value for `grpc-metadata-mm-model-id` should match the folder name of the model when it was downloaded and saved in `./models` in Step 3.
- The ${PUBLIC_ENDPOINT} value can be found with command `gcloud run services describe my-watson-nlp-runtime-rest --region=us-central1`.

If you get a response like the following, the REST service is working properly.

```json
{
  "text": "This is a test.",
  "producerId": {
    "name": "Izumo Text Processing",
    "version": "0.0.1"
  },
  "tokens": [
    {
      "span": {
        "begin": 0,
        "end": 4,
        "text": "This"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 5,
        "end": 7,
        "text": "is"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 8,
        "end": 9,
        "text": "a"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 10,
        "end": 14,
        "text": "test"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 14,
        "end": 15,
        "text": "."
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    }
  ],
  "sentences": [
    {
      "span": {
        "begin": 0,
        "end": 15,
        "text": "This is a test."
      }
    }
  ],
  "paragraphs": [
    {
      "span": {
        "begin": 0,
        "end": 15,
        "text": "This is a test."
      }
    }
  ]
}
```

## Clean up

Don't forget to clean up afterwards, to avoid paying for the cloud resources you no longer need.

Delete the gRPC service:

```sh
gcloud run services delete my-watson-nlp-runtime-grpc --region=us-central1
```

Delete the REST service:

```sh
gcloud run services delete my-watson-nlp-runtime-rest --region=us-central1
```

Delete the runtime image from Container Registry:

```sh
gcloud container images delete gcr.io/${GOOGLE_CLOUD_PROJECT}/my-watson-nlp-runtime:latest
```

