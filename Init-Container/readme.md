# Running Pretrained Watson NLP Models on Kubernetes or OpenShift

In this tutorial, you will serve Watson NLP pretrained models on a Kubernetes or OpenShift cluster. 

One possible approach to doing this is to build a standalone container image that packages the Watson NLP Runtime together with the models. This approach is the topic of another tutorial.  An advantage of a standalone container is that the same image can be run using Docker, a cloud container service, as well as Kubernetes or OpenShift. 

The downside of using standalone containers is that you need to build and manage a new container image every time there is a change in the set of models to be served. Moreover, the sizes of the container images can be large when there are many models to serve.

The present tutorial uses another approach that is specific to Kubernetes and OpenShift: In the Kubernetes manifest, the Pod specification uses the Watson NLP Runtime image as the main application image, and the pretrained model images to be served *init containers* of the Pod. Note that both the Watson NLP Runtime as well as Watson NLP pretrained models are available as container images on IBM's container registry.

Init container images will run to completion before the main application container runs. The images for the pretrained models specifically will provision the model to the *emptyDir* volume of the Pod, where they can be loaded by the Watson NLP Runtime.

Using this approach, models are kept in separate containers, that are themselves separate from the runtime. To change the set of served models you need only to update the Kubernetes manifest.

### Architecture diagram



### Prerequisites
- Python >= 3.9 installed on your local machine.  (This is needed to run the client program.)
- You have either the Kubernetes or OpenShift CLI (`kubectl` or `oc`) installed on your local machine.
- You have a Kubernetes or OpenShift cluster that you can use to deploy the service, and are logged in with the CLI. 

## Steps

### 1. Clone the GitHub repository
Clone the repository containing the code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
The code for this tutorial in under `Watson-NLP/Init-Container`.

### 2. Ensure that your cluster has access to the registry

### 3. Create the resource



### 4. Test the service
