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
A Kubernetes custom resource `Predictor` can be created for the uploaded model as follows.
```
oc create -f - <<EOF
apiVersion: wmlserving.ai.ibm.com/v1
kind: Predictor
metadata:
  name: $PREDICTOR
spec:
  modelType:
    name: watson-nlp
  path: $PATH-TO-MODEL
  storage:
    s3:
      secretKey: $BUCKET
      bucket: $BUCKET
EOF
```
Note:
- Replace `$PREDICTOR` with any unique name for the predictor.
- Replace `$PATH-TO-MODEL` with the folder path inside the bucket.
- Replace `$BUCKET` with the name of the COS bucket.

Once the model is successfully loaded, you'll see the status of the model is `Loaded`, when checked with the following command:
```
oc get predictor
```
