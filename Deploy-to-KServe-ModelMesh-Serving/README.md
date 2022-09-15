# Tutorial: Deploy a Watson NLP Model to KServe ModelMesh Serving
[KServe ModelMesh Serving](https://github.com/kserve/modelmesh-serving) is a Kubernetes-based platform for realtime serving of ML/DL models, optimized for high volume/density use cases. Utilization of available system resources is maximized via intelligent management of in-memory model data across clusters of deployed Pods, based on usage of those models over time. Leveraging existing third-party model servers, a number of standard ML/DL model formats are supported out-of-the box with more to follow: TensorFlow, PyTorch ScriptModule, ONNX, scikit-learn, XGBoost, LightGBM, OpenVINO IR. It can also be extended to support custom runtimes with arbitrary model formats, such as Watson NLP runtime.

This tutorial will walk you through the steps to deploy Watson NLP models to a KServe ModelMesh Serving sandbox environment on [IBM Technology Zone](https://techzone.ibm.com/) (or TechZone in short).

## Prerequisites
- Access to a KServe ModelMesh Serving sandbox environment on IBM Technology Zone
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli) (`ibmcloud`) and [IBM Cloud Kubernetes Service plug-in](https://cloud.ibm.com/docs/containers?topic=containers-cs_cli_install) (`ibmcloud ks`)
- Kubernetes command line tool [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Minio Client command line tool [mc](https://min.io/download)

## Sample Dash App
After you reserve a KServe ModelMesh Serving sandbox environment in TechZone, you'll receive an email with a link to the [Kubernetes Dashboard](https://github.com/kubernetes/dashboard), which shows the Kubernetes `service` resources in a dedicated `namespace` when you open it up in a browser. You should be able to find a `service` named `dash-app-lb`, that has an external endpoint. Click on the external endpoint would open up a sample Dash App in your browser. You can use this sample Dash App to send **Sentiment Analysis** and **Emotion Classification** inference requests to the ModelMesh Serving instance, by entering some text in the corresponding text input boxes and clicking on the `Get` buttons.

**Tip**:
- For new users, you would received an email invite from IBM Cloud to join the `tsglwatson` account.
- You need to login to the [IBM Cloud Console](https://cloud.ibm.com/docs/overview?topic=overview-ui) before you can open up the Kubernetes Dashboard.
- It might take a few minutes for the DNS record of the Dash App's external endpoint to propagate across the Internet.

### Login with CLI
You'll need to [login to the IBM Kubernetes Service (IKS) cluster](https://cloud.ibm.com/docs/containers?topic=containers-access_cluster) with the CLI tools to run the CLI commands in this tutorial.

<span style="font-size:x-small">

```
# Login to the IBM Cloud CLI. Enter your IBM Cloud credentials when prompted.
ibmcloud login

# Sets the context by updating the kubeconfig file set by KUBECONFIG environment variable, or ~/.kube/config by default.
ibmcloud ks cluster config --cluster iks-ksmm1v

# Set the default namespace in your current context.
kubectl config set-context --current --namespace=<insert-namespace-name-here>
```
</span>

**Tip**:
- The name of your dedicated `namespace` in the IKS cluster can be found in the email you received from TechZone.

### Sample models
Some sample Watson NLP stock models are loaded into the Watson NLP runtime pods, so that the serving instance can properly handle the API calls from the sample Dash App and send the results back. These sample models are stored in a shared read-only S3 compatible [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage) (COS) bucket. Some [Kubernetes custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) are created so that the serving instance knows how to load the sample models.

<span style="font-size:x-small">

```
$ kubectl get inferenceservice
NAME                                                    URL                                                       READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION   AGE
ensemble-classification-wf-en-emotion-stock-predictor   grpc://modelmesh-serving.ibmid-6620037hpc-669mq7e2:8033   True                                                                  93m
sentiment-document-cnn-workflow-en-stock-predictor      grpc://modelmesh-serving.ibmid-6620037hpc-669mq7e2:8033   True                                                                  93m
syntax-izumo-en-stock-predictor                         grpc://modelmesh-serving.ibmid-6620037hpc-669mq7e2:8033   True                                                                  93m
```
</span>

## Upload your own models to the COS bucket
The KServe ModelMesh Serving instance in TechZone comes with a dedicated COS bucket, where you can store your own models and serve them through the KServe ModelMesh Serving instance. Several CLI tools can be used to upload your models to the COS bucket. We'll use the Minio Client here as an example.

### Find the HMAC credential for the COS bucket
You'll need the [HMAC credential](https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-uhc-hmac-credentials-main) stored in a Kubernetes `secret` object named `storage-config` to access the COS bucket. Here's how you can retrieve it.

<span style="font-size:x-small">

```
kubectl get secret/storage-config -o json | jq -r '."data"."'$BUCKET'"' | base64 -d
```
</span>

**Note**:
- Replace `$BUCKET` with the name of the dedicated COS bucket, which should be the same as the Kubernetes namespace for your KServe ModelMesh Serving instance.

**Example**:

<span style="font-size:x-small">

```
$ kubectl get secret/storage-config -o json | jq -r '."data"."'$BUCKET'"' | base64 -d
{
    "type": "s3",
    "access_key_id": "683a3fb50e0a49d5ae2463725b3e83f5",
    "secret_access_key": "86b13e59da3a28d1b134d11ace6913705043c4289d976e37",
    "endpoint_url": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
    "region": "us-south",
    "default_bucket": "ibmid-6620037hpc-669mq7e2"
}
```
</span>

### Configure Minio Client
To add an entry in your Minio Client configuration for the COS bucket, run the following command:

<span style="font-size:x-small">

```
mc config host add $ALIAS $COS-ENDPOINT $ACCESS-KEY-ID $SECRET-ACCESS-KEY
```
</span>

**Note**:
- Replace `$ALIAS` with a short alias for referencing Object Storage in commands.
- Replace `$COS-ENDPOINT` with the `endpoint_url` of the HMAC credential.
- Replace `$ACCESS-KEY-ID` with the `access_key_id` of the HMAC credential.
- Replace `$SECRET-ACCESS-KEY` with the `secret_access_key` of the HMAC credential.

### Upload a model from a local directory to the COS bucket

<span style="font-size:x-small">

```
mc cp --recursive /path/to/mymodel mycos/mybucket/mymodel
```
</span>

More details regarding Minio and other tools can be found in the following IBM Cloud docs:
- https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-minio
- https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-upload

## Create a predictor for your model
A Kubernetes custom resource `InferenceService` with a `predictor` can be created for the uploaded model as follows.

<span style="font-size:x-small">

```
kubectl create -f - <<EOF
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: $NAME
  annotations:
    serving.kserve.io/deploymentMode: ModelMesh
spec:
  predictor:
    model:
      modelFormat:
        name: watson-nlp
      storage:
        path: $PATH-TO-MODEL
        key: $BUCKET
        parameters:
          bucket: $BUCKET
EOF
```
</span>

**Note**:
- Replace `$NAME` with any valid unique name.
- Replace `$PATH-TO-MODEL` with the folder path inside the bucket.
- Replace `$BUCKET` with the name of the COS bucket.

Once the model is successfully loaded, you'll see the `READY` status is `True`, when checked with the following command:

<span style="font-size:x-small">

```
kubectl get inferenceservice
```
</span>
