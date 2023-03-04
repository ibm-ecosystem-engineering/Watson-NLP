# Serve Watson NLP Models on a GKE Cluster with Knative

With IBM Watson NLP, IBM introduced a common library for natural language processing, document understanding, translation, and trust. IBM Watson NLP brings everything under one umbrella for consistency and ease of development and deployment. This tutorial will walk you through the steps to serve pretrained Watson NLP models with [Knative](https://knative.dev/docs/) deployed on a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster.

Knative is an open-source platform built on top of Kubernetes, designed to simplify the development and deployment of modern cloud-native applications by providing powerful tools for deploying, managing, and scaling serverless and event-driven workloads. Knative's autoscaling capabilities enable it to automatically scale serverless workloads up and down, even to zero, based on incoming traffic, which helps to reduce costs and improve application performance.

In this tutorial you will learn how to install Knative from scratch on a GKE cluster, and serve pretrained Watson NLP models through a couple of Knative Services created for Watson NLP Runtime.


## Prerequisites

- Your entitlement key to access the IBM Entitled Registry
- Access to a project in Google Cloud
- If you don't use Cloud Shell, make sure you have the following tools installed on your local machine:
  - [Docker](https://docs.docker.com/get-docker/)
  - [gcloud CLI](https://cloud.google.com/cli)
  - [grpcurl](https://github.com/fullstorydev/grpcurl/releases)

**Tip**:

- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.


## Deploy a GKE Standard Cluster

We'll first deploy a GKE Standard cluster for this tutorial. You could use an existing cluster, if you have cluster-admin access and enough resources in the cluster.

### Step 1: Launch Google Cloud Shell

[Cloud Shell](https://cloud.google.com/shell) is an interactive shell environment for Google Cloud that lets you learn and experiment with Google Cloud and manage your projects and resources from your web browser. With Cloud Shell, the Google Cloud CLI and other utilities you need are pre-installed, fully authenticated, up-to-date, and always available when you need them. You can also install additional packages and tools you need into the Cloud Shell environment.

If you have access to multiple Google Cloud projects, make sure the environment variable `GOOGLE_CLOUD_PROJECT` in Cloud Shell is set to the correct project. You can use the `gcloud config set project` command to switch project if necessary.

### Step 2: Create the cluster with gcloud CLI

Set the variables for the [region](https://cloud.google.com/about/locations) and cluster name of your choice:

```sh
MYREGION="<replace with a valid region>"
MYCLUSTER="<replace with the name of your cluster>"
```

Run the following command to create a Standard cluster:

```sh
gcloud container clusters create $MYCLUSTER \
    --region $MYREGION \
    --machine-type=e2-standard-8 \
    --release-channel None
```

It takes a few minutes for the cluster creation to complete. Once it's done, you can check it with the `gcloud container clusters list` command. The above `gcloud container clusters create` command also updates the kubeconfig file (set by environment variable `$KUBECONFIG`, or `$HOME/.kube/config` by default) with appropriate credentials and endpoint information to point `kubectl` to the newly created cluster.


## Install Knative using the Knative Operator

Knative provides a Kubernetes Operator to install, configure and manage Knative. You can install the Serving component, Eventing component, or both on your cluster. For the sake of this tutorial, we'll only install Knative Serving.

### Step 3: Install the Knative Operator

Run the command bellow to install the latest stable Operator release in the `default` namespace:

```sh
kubectl apply -n default -f https://github.com/knative/operator/releases/download/knative-v1.9.2/operator.yaml
```

### Step 4: Verify your Knative Operator installation

To check the Operator deployment status, use the following command:

```sh
kubectl get deployment knative-operator -n default
```

To track the log of the Operator, use the following command:

```sh
kubectl logs deploy/knative-operator -f -n default
```

### Step 5: Install Knative Serving

To install Knative Serving you must create a custom resource (CR), add a networking layer to the CR, and configure DNS.

Create the Knative Serving CR:

```sh
kubectl apply -f - <<EOF
---
apiVersion: v1
kind: Namespace
metadata:
  name: knative-serving
---
apiVersion: operator.knative.dev/v1beta1
kind: KnativeServing
metadata:
  name: knative-serving
  namespace: knative-serving
EOF
```

**NOTE:**
When you don't specify a version using `spec.version`, the Operator defaults to the latest version.

### Step 6: Install the networking layer

Knative Operator can configure the Knative Serving component with different networking layer options. Istio is the default networking layer if the ingress is not specified in the Knative Serving CR. If you choose the default Istio networking layer, you must install Istio on your cluster.

Download Istio 1.17.1 into a local directory, e.g., `$HOME/istio`:

```sh
mkdir -p ~/istio && cd ~/istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.17.1 TARGET_ARCH=x86_64 sh -
```

Create an alias for `istioctl` in the current shell:

```sh
alias istioctl=~/istio/istio-1.17.1/bin/istioctl
```

Install Istio on your cluster:

```sh
istioctl install -y
```

Fetch the External IP of the Istio [Ingress Gateway](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/):

```sh
kubectl get svc istio-ingressgateway -n istio-system
```

### Step 7: Configure DNS

Knative uses DNS names to decide where to route the incoming traffic. To configure DNS for Knative, take the External IP of the ingress gateway you get from the previous step, and create a wildcard `A` record with your DNS provider. For example:

```
*.knative.example.com     A 123.45.67.89
```

**TIP:**
- If you don't have the necessary privilege to create such a DNS record, you could use a record in the [hosts file](https://en.wikipedia.org/wiki/Hosts_(file)) on your local machine, or the `-H "Host:"` command-line option of the `curl` and `grpcurl` commands, to make REST and gRPC calls. For example:

        ```sh
        # With curl
        curl -H "Hosts: myservice.knative.example.com" http://123.45.67.89
        
        # With grpcurl
        grpcurl -H "Hosts: myservice.knative.example.com" 123.45.67.89:80
        ```

### Step 8: Verify the Knative Serving deployment

Monitor the Knative deployment:

```sh
kubectl get deployment -n knative-serving
```

If Knative Serving has been successfully deployed, all deployments of Knative Serving will show `READY` status. Here is a sample output:

```sh
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
activator               1/1     1            1           7m43s
autoscaler              1/1     1            1           7m42s
autoscaler-hpa          1/1     1            1           7m40s
controller              1/1     1            1           7m42s
domain-mapping          1/1     1            1           7m42s
domainmapping-webhook   1/1     1            1           7m41s
net-istio-controller    1/1     1            1           7m38s
net-istio-webhook       1/1     1            1           7m38s
webhook                 1/1     1            1           7m41s
```

Check the status of Knative Serving Custom Resource:

```sh
kubectl get KnativeServing knative-serving -n knative-serving
```

If Knative Serving is successfully installed, you should see an output like this:

```sh
NAME              VERSION   READY   REASON
knative-serving   1.9.0     True
```

### Step 10: Configure Knative Serving

The Knative Operator manages the configuration of a Knative installation, by propagating values from the `KnativeServing` and `KnativeEventing` custom resources to system ConfigMaps. Any manual updates to ConfigMaps are overwritten by the Operator. Knative has multiple ConfigMaps that are named with the `config-` prefix. All Knative ConfigMaps are created in the same namespace as the custom resource, which is `knative-serving` for Knative Serving. The `spec.config` in the Knative custom resources have one `<name>` entry for each ConfigMap, named `config-<name>`, the value of which is used for the ConfigMap `data`.

We'll update the following Knative Serving configuration settings:
- Specify the domain suffix for your Knative installation, e.g., `knative.example.com`.
- Specify the golang text template string to use when constructing a Knative service's DNS name: `"{{.Name}}-{{.Namespace}}.{{.Domain}}"`.
- Enable [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) support.
- Enable [emptyDir volume](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) support.

To apply the configuration, use the following command:

```sh
kubectl apply -f - <<EOF
apiVersion: operator.knative.dev/v1beta1
kind: KnativeServing
metadata:
  name: knative-serving
  namespace: knative-serving
spec:
  config:
    domain:
      knative.example.com: ""
    network:
      domain-template: "{{.Name}}-{{.Namespace}}.{{.Domain}}"
    features:
      kubernetes.podspec-init-containers: "enabled"
      kubernetes.podspec-volumes-emptydir: "enabled"
EOF
```


## Deploy Watson NLP Runtime with Pretrained Models

With Knative Serving installed and configured on your GKE cluster, it's time to deploy the Watson NLP Runtime as a [Knative Service](https://knative.dev/docs/serving/services/). In fact, we'll deploy two Knative service instances: one for gRPC, another for REST. More on that later.

### Step 11: Create a namespace

We'll create a dedicated namespace for deploying the two Knative services. For example:

```sh
kubectl create namespace watson
```

### Step 12: Create a Secret for the IBM Entitlement Key

The IBM Entitled Registry contains various container images for Watson NLP Runtime and pretrained models. You can obtain the entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary) and store it in a Kubenetes Secret resource, needed for your deployment to access those images.

The following command creates a secret named `ibm-entitlement-key` to store your IBM Entitlement Key.

```sh
kubectl create secret docker-registry ibm-entitlement-key \
  --docker-server=cp.icr.io/cp \
  --docker-username=cp \
  --docker-password=$IBM_ENTITLEMENT_KEY \
  -n watson
```

### Step 13: Clone the GitHub repository

Run the following command to clone the repository that contains the Knative Service manifests used in this tutorial:

```sh
git clone https://github.com/ibm-build-lab/Watson-NLP.git
```

Go to the directory of this tutorial:

```sh
cd Watson-NLP/MLOps/Deploy-to-GKE-with-Knative
```

### Step 14: Create the Knative Services

The Watson NLP Runtime runs both a gRPC server and a REST server, on port 8085 and port 8080 respectively. Since Knative Serving doesn't allow multiple ports in a service, we'll create two services instead, using the same Watson NLP Runtime and models, while each exposing a different port. In both Knative Service manifests, the Watson NLP pretrained model images are specified as [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/). These Init Containers run to completion before the main container starts in the Pod. They would provision models into an [emptyDir volume](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) defined in the Pod. When the Watson NLP Runtime container starts, it loads the models and begins serving them.

To create a Knative Service resource for the gRPC server, run the following command:

```sh
kubectl create -f watson-nlp-grpc-ksvc.yaml -n watson
```

To create a Knative Service resource for the REST server, run the following command:

```sh
kubectl create -f watson-nlp-rest-ksvc.yaml -n watson
```

It might take a few minutes for the `watson-nlp-runtime` container to be created. You can check the progress by watching the events:

```sh
kubectl get events -w -n watson
```

When a Knative Service is created, Knative creates a set of Kubernetes resources. This includes creating a Knative Configuration resource, which defines the desired state of the service, and an initial Knative Revision based on that configuration. Knative creates a Kubernetes Deployment resource to manage the scaling and replication of the service, and a Kubernetes Service resource to expose the service to other components within the Kubernetes cluster. Knative also creates an Istio Virtual Service and Knative Ingress to handle incoming traffic. Autoscaling is handled by Knative Pod Autoscaler (KPA), or by Kubernetes HPA with no scale-to-zero functionality. This complex orchestration provides an easy way to manage the deployment, scaling, and routing of a Knative Service, letting you focus on developing and delivering high-quality applications.


## Access the Knative Services

With the Watson NLP Runtime up and running, and its API services ready to accept incoming requests, you can make gRPC and REST calls using a command line utility like `grpcurl` and `curl` respectively.

### Step 15: Use grpcurl to make a gRPC call

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
FQDN=$(kubectl get ksvc watson-nlp-grpc-ksvc -n watson -o jsonpath="{.status.url}"|awk -F/ '{print $3}')
grpcurl -plaintext -proto common-service.proto -import-path ./protos \
  -H "mm-model-id: syntax_izumo_lang_en_stock" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ] }" \
  ${FQDN}:80 watson.runtime.nlp.v1.NlpService.SyntaxPredict \
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

### Step 16: Use curl to make a REST call

You can send inference requests to the REST service endpoint using `curl` commands.

Make a sample REST call:

```sh
URL=$(kubectl get ksvc watson-nlp-rest-ksvc -n watson -o jsonpath="{.status.url}")
curl -k -X POST "${URL}/v1/watson.runtime.nlp.v1/NlpService/SyntaxPredict" \
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

Delete the GKE cluster:

```sh
gcloud container clusters delete $MYCLUSTER --project $GOOGLE_CLOUD_PROJECT --region $MYREGION
```

