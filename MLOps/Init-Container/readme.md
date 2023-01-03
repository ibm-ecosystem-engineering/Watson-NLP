# Serve Pretrained Models on Kubernetes or OpenShift

In the tutorial you will serve Watson NLP pretrained models on a Kubernetes or OpenShift cluster. You will create a Kubernetes Deployment to run the Watson NLP Runtime image. In the Pods of this Deployment, pretrained model images are specified as _init containers_. These init containers will run to completion before the main application starts, and will provision models to the _emptyDir_ volume of the Pod. When the Watson NLP Runtime container starts it will load the models and begin serving them.

When using this approach, models are kept in separate containers from the runtime. To change the set of served models you need only to update the Kubernetes manifest.

Follow the [tutorial](https://developer.ibm.com/tutorials/serve-pretrained-models-on-kubernetes-or-openshift/) to learn how to serve Watson NLP pretrained models on a Kubernetes or OpenShift cluster.
