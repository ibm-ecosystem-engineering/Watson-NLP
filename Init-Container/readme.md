# Running Pretrained Watson NLP Models on Kubernetes or OpenShift

In this tutorial, you will serve Watson NLP pretrained models on a Kubernetes or OpenShift cluster. 

Rather than use a standalone container --- in which runtime and models are packaged into a single image --- this tutorial uses an approach specific to Kubernetes and OpenShift: In the Kubernetes manifest, the Pod specification uses the Watson NLP Runtime image as the main application image, and the pretrained model images to be served *init containers* of the Pod. Note that both the Watson NLP Runtime as well as Watson NLP pretrained models are available as container images on IBM's container registry.

Init container images will run to completion before the main application container runs. The images for the pretrained models specifically will provision the model to the *emptyDir* volume of the Pod, where they can be loaded by the Watson NLP Runtime.

Using this approach, models are kept in separate containers, that are themselves separate from the runtime. To change the set of served models you need only to update the Kubernetes manifest. 

### Architecture diagram



### Prerequisites
- Python >= 3.9 installed on your local machine.  (This is needed to run the client program.)
- You have a Kubernetes or OpenShift cluster that you can use to deploy the service. 
- You have either the Kubernetes or OpenShift CLI (`kubectl` or `oc`) installed on your local machine, and configured to use the cluster.

## Steps

### 1. Give your cluster access to the image registry
We will create a secret in the Kubernetes or OpenShift cluster that grants the cluster access to the IBM Entitled Registry, where the Watson NLP Runtime and pretrained models are stored.
```
docker login
```
... TODO ...

### 2. Get the sample code
Clone the GitHub repository containing the sample code used in this tutorial.  
```
git clone https://github.com/ibm-build-labs/Watson-NLP 
```
Go to the directory with code used in this tutorial.
``
cs Watson-NLP/Init-Container
``

### 2. Deploy the service
 


### 4. Test the service
