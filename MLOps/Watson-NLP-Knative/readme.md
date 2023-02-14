# Serve Watson MLP Models Using Knative Serving init-container method

With IBM Watson NLP, IBM introduced a common library for natural language processing, document understanding, translation, and trust. IBM Watson NLP brings everything under one umbrella for consistency and ease of development and deployment. This tutorial walks you through the steps to serve pretrained Watson NLP models using **Knative Serving** in a Red Hat OpenShift cluster.

**Knative Serving** is an Open-Source Enterprise-level solution to build Serverless and Event Driven Applications in Kubernetes / OpenShift cluster. For more information see [https://knative.dev/docs/](https://knative.dev/docs/).

In the tutorial, you create a `Knative Service` to run the Watson NLP runtime image. In the Knative Service Manifest, pretrained model images are specified as init containers. These init containers run to completion before the main application starts, and provision models to the emptyDir volume of the Pod. When the Watson NLP Runtime container starts, it loads the models and begins serving them.

When using this approach, models are kept in separate containers from the runtime. To change the set of served models you need only to update the Knative service Manifest.

## Prerequisites

To follow this tutorial, you need:

- [Docker Desktop](https://docs.docker.com/get-docker/) installed.
- You have access to an OpenShift Container Platform account with cluster administrator access. For this tutorial, you can reserve an [OpenShift Sandbox](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/reserve-openshift-sandbox).
  - If you are using your own cluster, please follow the below instructions to install Knative Serving. In this tutorial we will use the OpenShift Serverless Operator to install Knative Serving.
    - [Install the OpenShift Serverless Operator](https://docs.openshift.com/container-platform/4.10/serverless/install/install-serverless-operator.html)
    - [Install Knative Serving](https://docs.openshift.com/container-platform/4.10/serverless/install/installing-knative-serving.html)
- (Optional) The Knative CLI client ```kn``` can be used to simplify the deployment. [Install the Knative CLI](https://knative.dev/docs/client/install-kn/)
- Red Hat OpenShift CLI (```oc```) installed, and configured to talk to your cluster.
- Your Kubernetes or Red Hat OpenShift cluster namespace must have access to the [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-lab/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)

**Tip:** Podman provides a Docker-compatible command-line front end. Unless otherwise noted, all of the Docker commands in this tutorial should work for Podman if you alias the Docker CLI with the shell command:

```bash
alias docker=podman
```

## Steps

### Step 1. Enable `init-containers` and `volumes-emptydir` in Knative configuration

> Please skip this step if you had reserved a sandbox environment in [techzone](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/reserve-openshift-sandbox)

Save `config-features` config map in your current directory.

``sh
oc get configmap/config-features -n knative-serving -o yaml > config-feature.yaml

``

Modify the saved yaml `config-feature.yaml` with your favourite editor and add the following lines in the data section. Please do not modify any other section and content.

```yaml
apiVersion: v1
data:
  kubernetes.podspec-init-containers: enabled
  kubernetes.podspec-volumes-emptydir: enabled
```
> There is an example file `deployment/config-feature.yaml` in deployment directory for your reference.

Apply the configuration

```sh
oc apply -f config-feature.yaml 
```

### Step 2. Clone the GitHub repository

Clone the repository containing code used in this tutorial.

```sh
git clone https://github.com/ibm-build-labs/Watson-NLP
```

### Step 3. Deploy the service

In this step you will deploy the container image to Knative Serving. During the creation of a Service, Knative performs the following steps:

- Creates a new immutable revision for this version of the application.
- Creates a Route, Ingress, Service, and Load Balancer for your app.
- Automatically scales your pods up and down, including scaling down to zero active pods.

***To deploy execute the below command.***

 ```sh
  oc apply -f knative-service.yaml
  ```

***Check if the service is up and running***
  
  ```sh
  oc get configuration  
  ```
  
***Output:***
  
  ```sh
  NAME            LATESTCREATED         LATESTREADY           READY   REASON
  watson-nlp-kn   watson-nlp-kn-00001   watson-nlp-kn-00001   True    

  ```
  
***check revision***
  
  ```sh
  oc get revisions
  
  ```
  
***Get the service url***

  ```sh
  oc get ksvc watson-nlp-kn  -o jsonpath="{.status.url}"
  ```

***Set the SERVICE_URL***
  
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

### Step 5. Testing ML Model serving

Exceute the curl command to the inference service.

  ```sh
    curl -X POST "${SERVICE_URL}/v1/watson.runtime.nlp.v1/NlpService/ClassificationPredict" -H "accept: application/json" -H "grpc-metadata-mm-model-id: classification_ensemble-workflow_lang_en_tone-stock" -H "content-type: application/json" -d "{ \"rawDocument\": { \"text\": \"Watson nlp is awesome! works in knative\" }}"
  ```

### Conclusion

This tutorial walked you through the steps to to serve pretrained Watson NLP models using Knative serving on a Red Hat OpenShift cluster. Also you observed how the Knative autoscaling scale the pod to zero when there is no traffice and if there is a traffic how the pod spins up automatically. In the tutorial, you learned how to create a Knative Deployment to run the Watson NLP runtime image.
