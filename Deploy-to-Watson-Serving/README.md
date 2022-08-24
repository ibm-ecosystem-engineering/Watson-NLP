# Deploy an NLP Model to Watson Serving

## Upload a model to the COS bucket
If you create a Watson Serving instance in TechZone, it comes with an S3 compatible IBM Cloud Object Storage (COS) bucket, where you can store your own models and servce them through the Watson Serving instance. Serveral CLI tools can be used to upload your models to the COS bucket. We'll use the [Minio Client](https://min.io/download#/linux) here as an example.

### Find the HMAC credential for the COS bucket
You'll need the HMAC credential stored in a Kubernetes `secret` object named `storage-config` to access the bucket. Here's how you can retrieve it.
```
oc get secret/storage-config -o json | jq -r '."data"."'$BUCKET'"' | base64 -d
```
Note:
- Replace `$BUCKET` with the name of the COS bucket, which should be the same as the OpenShift project for your Watson Serving instance.

Example:
```
$ BUCKET=$(oc get project -o JSON | jq -r '.items[0]."metadata"."name"')
$ oc get secret/storage-config -o json | jq -r '."data"."'$BUCKET'"' | base64 -d
{
    "type": "s3",
    "access_key_id": "683a3fb50e0a49d5ae2463725b3e83f5",
    "secret_access_key": "86b13e59da3a28d1b134d11ace6913705043c4289d976e37",
    "endpoint_url": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
    "region": "us-south",
    "default_bucket": "ibmid-6620037hpc-669mq7e2"
}
```

### Configure Minio Client
To add an entry in your Minio Client configiuration for the COS bucket, run the following command:
```
mc config host add $ALIAS $COS-ENDPOINT $ACCESS-KEY-ID $SECRET-ACCESS-KEY
```
Note:
- Replace `$ALIAS` with a short alias for referencing Object Storage in commands.
- Replace `$COS-ENDPOINT` with the `endpoint_url` of the HMAC credential.
- Replace `$ACCESS-KEY-ID` with the `access_key_id` of the HMAC credential.
- Replace `$SECRET-ACCESS-KEY` with the `secret_access_key` of the HMAC credential.

### Upload a model from a local directory to the COS bucket
```
mc cp --recursive /path/to/mymodel mycos/mybucket/mymodel
```

More details regarding Minio and other tools can be found in the following IBM Cloud docs:
- https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-minio
- https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-upload

## Create a predictor
A Kubernetes custom resource `InferenceService` with a `predictor` can be created for the uploaded model as follows.
```
oc create -f - <<EOF
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
Note:
- Replace `$NAME` with any valid unique name.
- Replace `$PATH-TO-MODEL` with the folder path inside the bucket.
- Replace `$BUCKET` with the name of the COS bucket.

Once the model is successfully loaded, you'll see the `READY` status is `True`, when checked with the following command:
```
oc get inferenceservice
```
