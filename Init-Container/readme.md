# Running Pretrained Watson NLP Models on Kubernetes or OpenShift

In this tutorial, you will run Watson NLP pretrained models on a Kubernetes or OpenShift cluster. 

One approach to doing so is to build a standalone container image to package both the Watson NLP Runtime together with the models. This approach is covered in a separate tutorial. An advantage of such a standalone container is that it can be run using Docker, a cloud container service, as well as Kubernetes or OpenShift. 

The downsides of using standalone containers is that you need to build and manage a new container image every time there is a change in the set of models to be served. Moreover, the sizes of the container images can be large when there are many models to serve.

This tutorial takes an alternative approach that is specific to running on a Kubernetes or OpenShift cluster. Watson NLP pretrained models are available as container images on IBM's container registry. You can create a Kubernetes Deployment to 

### Architecture diagram

### Prerequisites

## Steps

### 1. Clone the GitHub repository
Clone the repository containing the code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
