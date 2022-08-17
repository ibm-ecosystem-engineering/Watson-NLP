# Deploy an NLP Model to Watson Serving

1. Upload a model to a COS bucket

https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-upload

2. Create an HMAC credential for accessing the bucket

https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-uhc-hmac-credentials-main&interface=cli#uhc-hmac-credentials-defined

3. Create a JSON file, e.g. mybucket.json
{
    "type": "s3",
    "access_key_id": "$ACCESS_KEY_ID",
    "secret_access_key": "$SECRET_ACCESS_KEY",
    "endpoint_url": "$ENDPOINT",
    "region": "$LOCATION",
    "default_bucket": "$BUCKET"
}

Note:
- Replace $ACCESS_KEY_ID and $SECRET_ACCESS_KEY with the actual values of the HMAC credential created in the previous step.
- Replace the $ENDPOINT with the appropriate value for your COS bucket.
- Replace $LOCATION with the location of your COS bucket.
- Replace $BUCKET with the name of your COS bucket.

4. Update secret/storage-config
oc patch secret/storage-config -p '{"data": {"$KEY": "'"$(cat mybucket.json | base64 -w0)"'"}}'

Note:
- Replace $KEY with any unique name you pick for the credential, such as the bucket name.

5. Create a predictor
oc create -f - <<EOF
apiVersion: wmlserving.ai.ibm.com/v1
kind: Predictor
metadata:
  name: $PREDICTOR
spec:
  modelType:
    name: watson-nlp
  path: $PATHTOMODEL
  storage:
    s3:
      secretKey: $KEY
      bucket: $BUCKET
EOF

Note:
- Replace $PREDICTOR with any unique name for the predictor
- Replace $PATHTOMODEL with the folder path in the bucket where your model is stored.
- Replace $KEY with the name you picked in previous step.
- Replace $BUCKET with the name of your COS bucket.

Once the model is successfully loaded, you'll see the status of the model is "Loaded", when checked with the following command:
oc get predictor
