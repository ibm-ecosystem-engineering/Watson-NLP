# Accessing Watson NLP Assets

This document describes how to access Watson NLP container images and other assets.

## Watson NLP Runtime and Pretrained Models

The Watson NLP Runtime and Pretrained Models are stored in Artifactory. To gain access you will need an [API key](https://na.artifactory.swg-devops.com/ui/admin/artifactory/user_profile).

### Docker

```
docker login https://na.artifactory.swg-devops.com
```
Enter your Artifactory user profile and API key at the prompts.

### Kubernetes



## Watson NLP Client SDKs

### Python
The Watson NLP Python Client SDK is stored in [PyPI](https://pypi.org/). Install it with the following command.
```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ watson-nlp-runtime-client
```
