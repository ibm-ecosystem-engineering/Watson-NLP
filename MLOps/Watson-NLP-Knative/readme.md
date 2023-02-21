# Serve Watson MLP Models Using Knative Serving 

With IBM Watson NLP, IBM introduced a common library for natural language processing, document understanding, translation, and trust. IBM Watson NLP brings everything under one umbrella for consistency and ease of development and deployment. This tutorial walks you through the steps to serve pretrained Watson NLP models using Knative Serving in a Red Hat OpenShift cluster.

Knative Serving is an Open-Source Enterprise-level solution to build Serverless and Event Driven Applications in Kubernetes / OpenShift cluster. For more information see [https://knative.dev/docs/](https://knative.dev/docs/).

A *Knative Service* is conceptually similar to a Kubernetes Deployment. In this tutorial you will create a Knative Service to run the Watson NLP Runtime. In the Knative Service Manifest pretrained Watson NLP model images are specified as init containers. These init containers run to completion before the main application starts, and provision models to the emptyDir volume of the Knative Service. When the Watson NLP Runtime container starts, it loads the models and begins serving them.

Using approach allows for models to be kept in separate container images from the runtime container image. To change the set of served models you need only to update the Knative Service Manifest.

## Prerequisites

- Install [Docker Desktop](https://docs.docker.com/get-docker/).
- Ensure that you have access to an OpenShift Container Platform account with cluster administrator access. 
  - For this tutorial, you can reserve a [Sandbox Environment](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/reserve-openshift-sandbox).
  - Alternatively, if you are using your own cluster, follow the instructions below to install Knative Serving.
    - [Install the OpenShift Serverless Operator](https://docs.openshift.com/container-platform/4.10/serverless/install/install-serverless-operator.html)
    - [Install Knative Serving](https://docs.openshift.com/container-platform/4.10/serverless/install/installing-knative-serving.html)
- Install the Red Hat OpenShift CLI (```oc```) and log in to your OpenShift cluster.
- Create a Docker registry secret in the Kubernetes project that grants access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-lab/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)

**Tip:** Podman provides a Docker-compatible command-line front end. Unless otherwise noted, all of the Docker commands in this tutorial should work for Podman if you alias the Docker CLI with the shell command:

```bash
alias docker=podman
```

## Steps

### Step 1. Configure Knative

> Skip this step if you are using the [Sandbox Environment](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/reserve-openshift-sandbox).

The deployment approach that we use in this tutorial relies on capabilities of Knative Serving that are disabled by default. Below you will configure Knative Service to enable *init containers* and *empty directories*.

Save `config-features` config map in your current directory.

```sh
oc get configmap/config-features -n knative-serving -o yaml > config-feature.yaml

```

Modify the configuration with your favourite editor by adding the following lines in the data section. Do not modify any other section and content.

```yaml
apiVersion: v1
data:
  kubernetes.podspec-init-containers: enabled
  kubernetes.podspec-volumes-emptydir: enabled
```

There is an example file `deployment/config-feature.yaml` in deployment directory for your reference.

Apply the configuration.

```sh
oc apply -f config-feature.yaml 
```

### Step 2. Clone the GitHub repository

Clone the repository containing code used in this tutorial.

```sh
git clone https://github.com/ibm-build-labs/Watson-NLP
cd Watson-NLP/MLOps/Watson-NLP-Knative/deployment
```

### Step 3. Create a Knative Service

In this step you will create a Knative Service to run the Watson NLP Runtime. When a Service is created, Knative does the following:

- It creates a new immutable revision for this version of the application.
- It creates a Route, Ingress, Service, and Load Balancer for your application.
- It automatically scales replicas based on request load, including scaling to zero active replicas.

To create the Service, run the following command.

 ```sh
  oc apply -f knative-service.yaml
  ```

Verify that the service has been created.
  
  ```sh
  oc get configuration  
  ```
  
You should see output similar to the following.
  
  ```sh
  NAME            LATESTCREATED         LATESTREADY           READY   REASON
  watson-nlp-kn   watson-nlp-kn-00001   watson-nlp-kn-00001   True    

  ```
  
To check the revisions of this service:
  
  ```sh
  oc get revisions
  
  ```

Set the URL for the Service in an environment variable.
  
  ```sh
  export SERVICE_URL=$(oc get ksvc watson-nlp-kn  -o jsonpath="{.status.url}")
  ```

### Step 4. Testing Knative autoscaling
  
With Knative autoscaling, code runs when it needs to, with Knative starting and stopping instances automatically. When there is no traffic no instance will be running of the app.
  
lets Check currently running pods

  ```sh
  oc get pods
  ```

You should not see any pod runnng. If you see the 'watson-nlp-kn' is running wait for a minute and the instance should be terminated automatically.
  
#### Observe the pod status changing

  Open a new terminal to exceute the below command to watch pod status changing

  ```sh
  oc get pods -w
  ```
  
  In the current terminal run the below commands to put some traffice in the service,
  
  ```sh
  curl ${SERVICE_URL}
  ```
  
  Observe the status of the pod. When you put some traffic, pod started to wake up and then after a while it got terminated automatically.

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

### Step 5. Testing inference service

Exceute the curl command to the inference service.

  ```sh
    curl -X POST "${SERVICE_URL}/v1/watson.runtime.nlp.v1/NlpService/ClassificationPredict" -H "accept: application/json" -H "grpc-metadata-mm-model-id: classification_ensemble-workflow_lang_en_tone-stock" -H "content-type: application/json" -d "{ \"rawDocument\": { \"text\": \"Watson nlp is awesome! works in knative\" }}"
  ```

### Conclusion

This tutorial walked you through the steps to to serve pretrained Watson NLP models using Knative serving on a Red Hat OpenShift cluster. Also you observed how the Knative autoscaling scale the pod to zero when there is no traffice and if there is a traffic how the pod spins up automatically. In the tutorial, you learned how to create a Knative Deployment to run the Watson NLP runtime image.
