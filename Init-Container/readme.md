# Running Pretrained Watson NLP Models on Kubernetes or OpenShift

In this tutorial, you will run Watson NLP pretrained models on a Kubernetes or OpenShift cluster. 

A separate tutorial uses the approach of building a standalone container image to package both the Watson NLP Runtime together with the models. An advantage of such a standalone container is that it can be run using Docker, a cloud container service, as well as Kubernetes or OpenShift. 

The downside of using standalone containers is that you need to build and manage a new container image every time there is a change in the set of models to be served. Moreover, the sizes of the container images can be large when there are many models to serve.

The present tutorial uses an alternative approach that is specific to Kubernetes or OpenShift. Both the Watson NLP Runtime as well as Watson NLP pretrained models are available as container images on IBM's container registry. In the Kubernetes manifest, the Pod specification uses the Watson NLP Runtime image as the main application image. The pretrained model images to be served are given as *init containers* of the Pod. 

Init container images will run to completion before the main application container runs. The images for the pretrained models specifically will provision the model to the *emptyDir* volume of the Pod, where they can be loaded by the Watson NLP Runtime.

### Architecture diagram

### Prerequisites

## Steps

### 1. Clone the GitHub repository
Clone the repository containing the code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
