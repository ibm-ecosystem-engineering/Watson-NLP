# Access Watson NLP Assets

This document describes how to access Watson NLP container images and other assets.

## Watson NLP Runtime and Pretrained Models

The Watson NLP Runtime and Pretrained Models are stored in Artifactory. To gain access you will need an [API key](https://na.artifactory.swg-devops.com/ui/admin/artifactory/user_profile). 

### Docker
Run the following command to allow Docker to access the images.
```
docker login wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com
```
Enter your Artifactory user profile and API key at the prompts.

### Kubernetes and OpenShift
To allow your Kubernetes or OpenShift cluster to access the container images, you can use the methods from the [Kubernetes documentation](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) to store your credentials as a Kubernetes Secret. 

For example, use the following command to create a Secret named `regcred`.
```
kubectl create secret docker-registry regcred --docker-server=wcp-ai-foundation-team-docker-virtual.artifactory.swg-devops.com --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email>
```
Where:
- `<your-name>` is your Artifactory user profile
- `<you-pword>` is your Artifactory API key
- `<your-email>` is your email address

## Watson NLP Client Libraries
The Watson NLP Runtime client libraries can be used by client programs to make inference requests against models that are being served using the Watson NLP Runtime.  Example code can be found [here](https://github.com/IBM/ibm-watson-embed-clients/tree/main/watson_nlp).

### Python
[Python 3.9](https://www.python.org/downloads/) or later is required to install.
```
pip install watson-nlp-runtime-client
```

### Node
```
npm i @ibm/watson-nlp-runtime-client
```

## Model Packager
This tool is used to package custom trained models into container images in the same way as are the Watson NLP pretrained models. It is stored on public [PyPI](https://pypi.org/).
```
pip install watson-embed-model-packager
```
