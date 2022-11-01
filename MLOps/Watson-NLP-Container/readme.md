# Serve Pretrained Models with a Standalone Container

This tutorial will walk you through the steps to build a container image to serve pretrained Watson NLP models, and to run it with Docker. The container image will include both the Watson NLP Runtime and the models.  When the container runs it will expose REST and gRPC endpoints that client programs can use to make inference requests on the models. 

These containers can run anywhere. In the tutorial you will run the container using Docker. The same image could also be run on a Kubernetes or OpenShift cluster; or on a cloud container service like IBM Code Engine or AWS Fargate.

Follow the [tutorial](https://developer.ibm.com/tutorials/serve-pretrained-models-with-a-standalone-container) to learn how to serve pretrained Watson NLP models by building a container image that contains both the Watson NLP runtime together with the pretrained models.
