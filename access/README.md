# Accessing Watson NLP Assets

This document describes how to access Watson NLP container images and other assets.

## Watson NLP Runtime and Pretrained Models

The Watson NLP Runtime and Pretrained Models are stored in Artifactory. To gain access you will need an [API key](https://na.artifactory.swg-devops.com/ui/admin/artifactory/user_profile).

### Docker
Run the following command to allow Docker to access the images.
```
docker login https://na.artifactory.swg-devops.com
```
Enter your Artifactory user profile and API key at the prompts.

### Kubernetes and OpenShift
To allow your Kubernetes or OpenShift cluster to access the container images, 

## Watson NLP Client SDKs
### Python
The Watson NLP Python Client SDK is stored in [PyPI](https://pypi.org/). Install it with the following command.
```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ watson-nlp-runtime-client
```
Note that the above command is only for when the SDK is in the test area. Once it is pushed to the public PyPI you will use the command:
```
pip install watson-nlp-runtime-client
```
## Model Packager
This tool is used to package custom trained models into container images in the same way as are the Watson NLP pretrained models. 
```
pip install watson-embed-model-packager
```
