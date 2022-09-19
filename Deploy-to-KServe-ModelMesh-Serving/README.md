# Deploy a Watson NLP Model to KServe ModelMesh Serving
This tutorial will walk you through the steps to deploy Watson NLP models to a KServe ModelMesh Serving sandbox environment on [IBM Technology Zone](https://techzone.ibm.com/) (TechZone).  

[Kserve](https://kserve.github.io/website/0.9/) is a Kubernetes based platform for ML model inference. It supports several standard ML model formats out-of-the-box including: TensorFlow, PyTorch ScriptModule, ONNX, scikit-learn, XGBoost, LightGBM, OpenVINO IR. It can also be extended to support custom runtimes with arbitrary model formats, such as Watson NLP runtime. 

[KServe ModelMesh Serving](https://kserve.github.io/website/0.7/modelserving/mms/modelmesh/overview/) is a recently added feature intended to increase Kserve's scalability.  It is designed to handle large volumes of models, where the deployed models change frequently.  It loads and unloads models aiming to balance between responsiveness to users, and computational footprint.

## Prerequisites
- Access to a KServe ModelMesh Serving sandbox environment on IBM Technology Zone
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli) (`ibmcloud`) and [IBM Cloud Kubernetes Service plug-in](https://cloud.ibm.com/docs/containers?topic=containers-cs_cli_install) (`ibmcloud ks`)
- Kubernetes command line tool [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Minio Client command line tool [mc](https://min.io/download)

## Getting started
When you first request a TechZone environment for Kserve ModelMesh Serving, the system will create a `namespace` for you in a Kubernetes cluster and deploy an instance of Kserve Model Mesh in the namespace.  Once your environment is ready, you will recieve an email to let you know.  This email will include a link to a [Kubernetes Dashboard](https://github.com/kubernetes/dashboard).  Clicking on this link will bring up the Kubernetes `service` resources in your dedicated `namespace`. 

Your TechZone environment will have an example Watson NLP application already running.  In your Kubernetes Dashboard find the `service` called `dash-app-lb`.  This application has an external endpoint. Clicking on the external endpoint will let you test this application in your browser. The application allows the user to feed in texts, and get back **Sentiment Analysis** and **Emotion Classification** on these texts texts. The models are being served by Kserve Model Mesh in your namespace.

**Tip**:
- For new users, you will receive an email invite from IBM Cloud to join the `tsglwatson` account when you first request the TechZone environment.
- You need to login to the [IBM Cloud Console](https://cloud.ibm.com/docs/overview?topic=overview-ui) before you can open up the Kubernetes Dashboard.
- It might take a few minutes for the DNS record of the Dash App's external endpoint to propagate across the Internet.

### Login with CLI
You will need to [login to the IBM Kubernetes Service (IKS) cluster](https://cloud.ibm.com/docs/containers?topic=containers-access_cluster) with the CLI tools to run the CLI commands in this tutorial.

<span style="font-size:x-small">

```
# Login to the IBM Cloud CLI with a one-time passcode. Enter your IBM Cloud credentials when prompted in the browser.
ibmcloud login --sso

# Set the context by updating the kubeconfig file set by KUBECONFIG environment variable, or ~/.kube/config by default.
ibmcloud ks cluster config --cluster <iks-cluster-name>

# Set kubectl to use your namespace by default.
kubectl config set-context --current --namespace=<your-namespace>
```
</span>

**Tip**:
- The names of the IKS cluster and your `namespace` can be found in the email you received from TechZone.

### Sample models
In order to serve a model using Kserve Model Mesh, store the model must be stored in an S3 compatible object store, and then create the Kuberneteds custom resource `inferenceservice` to register the model with the service.  
    
In the TechZone sandbox environment, the Watson NLP models that are used by the example application are stored in a shared read-only S3 compatible [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage) (COS) bucket, and `inferenceservice` CRs have been created for these models. 

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
You will need the [HMAC credential](https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-uhc-hmac-credentials-main) stored in a Kubernetes `secret` object named `storage-config` to access the COS bucket. Here is how you can retrieve it.

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
A Kubernetes custom resource `InferenceService` is created for the uploaded model as follows.

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

Once the model is successfully loaded, you will see the `READY` status is `True`, when checked with the following command:

<span style="font-size:x-small">

```
kubectl get inferenceservice
```
</span>
