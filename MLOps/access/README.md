# Access Watson NLP Assets

This document describes how to access Watson NLP container images and other assets.

## Watson NLP Runtime and Pretrained Models

The Watson NLP Runtime and Pretrained Models are stored in IBM Entitled Registry. To gain access you will need an entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary). You can [sign up for a free trial using this form](https://www.ibm.com/account/reg/us-en/subscribe?formid=urx-51726). Set the environment variable `IBM_ENTITLEMENT_KEY` to your entitlement key.

### Docker

Run the following command.

```sh
echo $IBM_ENTITLEMENT_KEY | docker login -u cp --password-stdin cp.icr.io
```

### Kubernetes and OpenShift

To allow your Kubernetes or OpenShift cluster to access the container images, you can use the methods from the [Kubernetes documentation](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) to store your credentials as a Kubernetes Secret.

Use the following command to create a Secret named `watson-nlp` in the namespace in which you want to deploy the Watson NLP Runtime or pretrained models.

```sh
kubectl create secret docker-registry watson-nlp --docker-server=cp.icr.io/cp --docker-username=cp --docker-password=$IBM_ENTITLEMENT_KEY
```

Once the secret is created, you can add an `imagePullSecrets` section to Pods.

```yaml
      imagePullSecrets:
      - name: watson-nlp
```

## Watson NLP Client Libraries

The Watson NLP Runtime client libraries can be used by client programs to make inference requests against models that are being served using the Watson NLP Runtime. Example code can be found [here](https://github.com/IBM/ibm-watson-embed-clients/tree/main/watson_nlp).

### Python

[Python 3.9](https://www.python.org/downloads/) or later is required to install.

```sh
pip install watson-nlp-runtime-client
```

### Node

```sh
npm i @ibm/watson-nlp-runtime-client
```

## Model Packager

This tool is used to package custom trained models into container images in the same way as are the Watson NLP pretrained models. These images can be hosted on a container registry and then specified as init containers of Pods, when serving models on a Kubnernetes or OpenShift cluster.

To install:

```sh
pip install watson-embed-model-packager
```

For usage information see the GitHub [repository](https://github.com/IBM/ibm-watson-embed-model-builder).
