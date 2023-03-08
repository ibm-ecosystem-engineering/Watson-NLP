# Serve Watson NLP Models with Google Kubernetes Engine

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) provides a managed environment for deploying, managing, and scaling your containerized applications using Google infrastructure. GKE's [Autopilot mode](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview) is a hands-off, fully managed Kubernetes platform that delivers a complete Kubernetes experience without you needing to configure or monitor your cluster’s underlying compute infrastructure. With per-pod billing, Autopilot ensures you pay only for your running pods, not system components, operating system overhead, or unallocated capacity for up to 85% savings from resource and operational efficiency.

This tutorial will walk you through the steps to deploy Watson NLP Runtime on a GKE Autopilot Cluster to serve a couple of pretrained models.


## Prerequisites

- Your entitlement key to access the IBM Entitled Registry
- Access to a project in Google Cloud
- If you don't use Cloud Shell, make sure you have the following tools installed on your local machine:
  - [Docker](https://docs.docker.com/get-docker/)
  - [gcloud CLI](https://cloud.google.com/cli)
  - [grpcurl](https://github.com/fullstorydev/grpcurl/releases)

**Tip**:

- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.


## Deploy a GKE Autopilot Cluster

We choose to deploy a GKE Autopilot cluster in this tutorial, mainly because it's simple and cost effective. You could use an existing GKE Autopilot or Standard cluster, as long as it allows you to deploy applications in a namespace and expose services for external access.

### Step 1: Launch Google Cloud Shell

[Cloud Shell](https://cloud.google.com/shell) is an interactive shell environment for Google Cloud that lets you learn and experiment with Google Cloud and manage your projects and resources from your web browser. With Cloud Shell, the Google Cloud CLI and other utilities you need are pre-installed, fully authenticated, up-to-date, and always available when you need them. You can also install additional packages and tools you need into the Cloud Shell environment.

If you have access to multiple Google Cloud projects, make sure the environment variable `GOOGLE_CLOUD_PROJECT` in Cloud Shell is set to the correct project. You can use the `gcloud config set project` command to switch project if necessary.

### Step 2: Create the cluster with gcloud CLI

Set the variables for the [region](https://cloud.google.com/about/locations) and cluster name of your choice:

```sh
MYREGION="<replace with a valid region>"
MYCLUSTER="<replace with the name of your cluster>"
```

Run the following command to create an Autopilot cluster:

```sh
gcloud container clusters create-auto $MYCLUSTER --project $GOOGLE_CLOUD_PROJECT --region $MYREGION
```

It takes a few minutes for the cluster creation to complete. Once it's done, you can check it with the `gcloud container clusters list` command. The above `gcloud container clusters create-auto` command also updates the kubeconfig file (set by environment variable `$KUBECONFIG`, or `$HOME/.kube/config` by default) with appropriate credentials and endpoint information to point `kubectl` to the newly created cluster.


## Deploy Watson NLP Runtime with Pretrained Models

The IBM Entitled Registry contains various container images for Watson NLP Runtime and pretrained models. You can obtained the entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary) for accessing those images.

### Step 3: Create a Secret for the IBM Entitlement Key

Kubenetes uses [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) to store sensitive data such as passwords, tokens, or keys. You can use the following command to create a Secret named `ibm-entitlement-key` for your IBM Entitlement Key.

```sh
kubectl create secret docker-registry ibm-entitlement-key \
  --docker-server=cp.icr.io/cp \
  --docker-username=cp \
  --docker-password=$IBM_ENTITLEMENT_KEY
```

### Step 4: Create a TLS certificate

TLS is often required to secure communication over untrusted networks. A TLS certificate needs to be created before enabling TLS. For the sake of this tutorial, we'll use a self-signed TLS certificate, as opposed to one issued by a trusted Certificate Authority (CA).

Run the following command to generate the self-signed TLS certificate and private key:

```sh
openssl req -x509 -newkey rsa:4096 -nodes -sha256 -days 365 \
  -subj '/CN=localhost' -extensions san -config openssl-san.conf \
  -keyout tls.key -out tls.crt
```

Where the content of `openssl-san.conf` looks like:

```conf
[req]
distinguished_name = req
[san]
subjectAltName = DNS:localhost
```

Run the following command to store the TLS certificate and private key in a Secret:

```sh
kubectl create secret tls watson-runtime-cert --cert=tls.crt --key=tls.key
```

### Step 5: Clone the GitHub repository

Run the following command to clone the repository that contains the Kubernetes manifests used later in this tutorial:

```sh
git clone https://github.com/ibm-build-lab/Watson-NLP.git
```

Go to the directory of this tutorial:

```sh
Watson-NLP/MLOps/Deploy-to-Google-Kubernetes-Engine
```

### Step 6: Create a Deployment

The following command creates a Kubernetes [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) resource for Watson NLP Runtime, with a couple of models copied into a [Volume](https://kubernetes.io/docs/concepts/storage/volumes/) using [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/):

```sh
kubectl create -f deployment/deployment.yaml
```

It might take a few minutes for the `watson-nlp-runtime` container to be created. You can check the progress by watching the events:

```sh
kubectl get events -L app:watson-nlp-runtime -w
```

Once the container is created, you can check its log messages:

```sh
kubectl logs deployment/watson-nlp-runtime -c watson-nlp-runtime -f
```

### Step 7: Create a Service

By default, Watson NLP Runtime starts the gRPC server on port 8085, and the REST server on port 8080. Run the following command to create a Kubernetes [Service](https://kubernetes.io/docs/concepts/services-networking/service/) resource to expose both ports of the network service:

```sh
kubectl create -f deployment/service.yaml
```

The created Kubernetes Service uses an external load-balancer, as `type: LoadBalancer` suggests in its Kubernetes manifest. It might take a few minutes for the external load-balancer to become ready to accept network connections, at the IP address and port listed by the `kubectl get service watson-nlp-runtime-service` command under `EXTERNAL-IP` and `PORT(S)`, as shown in the following example:

```sh
$ kubectl get service watson-nlp-runtime-service
NAME                         TYPE           CLUSTER-IP   EXTERNAL-IP      PORT(S)                         AGE
watson-nlp-runtime-service   LoadBalancer   10.7.131.0   34.123.153.123   8080:31825/TCP,8085:30357/TCP   1h34m
```

## Access the Watson NLP API Services

With the Watson NLP Runtime up and running, and its API services ready to accept incoming requests, you can make gRPC and REST calls using a command line utility like `grpcurl` and `curl` respectively.

### Step 8: Use grpcurl to make a gRPC call

You can send inference requests to the gRPC service endpoint using `grpcurl` commands. Either a [Protocol Buffers](https://protobuf.dev/) source file specified by `-proto`, or a compiled "protoset" file specified by `-protoset`, is needed for making gRPC calls to a gRPC service that doesn't provide gRPC [server reflection](https://github.com/grpc/grpc/blob/master/doc/server-reflection.md).

The proto source files can be extracted from the Watson NLP Runtime container image as follows:

```sh
docker run -d --rm --name watson-nlp-runtime \
  -e ACCEPT_LICENSE=true \
  cp.icr.io/cp/ai/watson-nlp-runtime:1.1.0 sleep 100
docker cp watson-nlp-runtime:/app/protos .
```

Make a sample gRPC call:

```sh
PUBLIC_ENDPOINT="${EXTERNALIP}:8085"
grpcurl -insecure -proto common-service.proto -import-path ./protos \
  -H "mm-model-id: syntax_izumo_lang_en_stock" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ] }" \
  ${PUBLIC_ENDPOINT} watson.runtime.nlp.v1.NlpService.SyntaxPredict \
  | jq -r .
```

**Tip**:

- The metadata value for `mm-model-id` is the Model ID of the pretrained model found in the [Models Catalog](https://www.ibm.com/docs/en/watson-libraries?topic=models-catalog).

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

### Step 9: Use curl to make a REST call

You can send inference requests to the REST service endpoint using `curl` commands.

Make a sample REST call:

```sh
PUBLIC_ENDPOINT="https://${EXTERNALIP}:8080"
curl -k -X POST "${PUBLIC_ENDPOINT}/v1/watson.runtime.nlp.v1/NlpService/SyntaxPredict" \
  -H "accept: application/json" \
  -H "grpc-metadata-mm-model-id: syntax_izumo_lang_fr_stock" \
  -H "content-type: application/json" \
  -d "{ \"rawDocument\": { \"text\": \"C'est un test.\" }, \"parsers\": [ \"TOKEN\" ] }" \
  | jq -r .
```

**Tip**:

- The metadata value for `grpc-metadata-mm-model-id` is the Model ID of the pretrained model found in the [Models Catalog](https://www.ibm.com/docs/en/watson-libraries?topic=models-catalog).

If you get a response like the following, the REST service is working properly.

```json
{
  "text": "C'est un test.",
  "producerId": {
    "name": "Izumo Text Processing",
    "version": "0.0.1"
  },
  "tokens": [
    {
      "span": {
        "begin": 0,
        "end": 2,
        "text": "C'"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 2,
        "end": 5,
        "text": "est"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 6,
        "end": 8,
        "text": "un"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 9,
        "end": 13,
        "text": "test"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 13,
        "end": 14,
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
        "end": 14,
        "text": "C'est un test."
      }
    }
  ],
  "paragraphs": [
    {
      "span": {
        "begin": 0,
        "end": 14,
        "text": "C'est un test."
      }
    }
  ]
}
```

## Clean up

Don't forget to clean up afterwards, to avoid paying for the cloud resources you no longer need.

Delete the Kubernetes Service resource:

```sh
kubectl delete -f deployment/service.yaml
```

Delete the Kubernetes Deployment resource:

```sh
kubectl delete -f deployment/deployment.yaml
```

Delete the GKE cluster:

```sh
gcloud container clusters delete $MYCLUSTER --project $GOOGLE_CLOUD_PROJECT --region $MYREGION
```

