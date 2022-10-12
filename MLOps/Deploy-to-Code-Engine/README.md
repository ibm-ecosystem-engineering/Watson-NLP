# Deploy Models on IBM Cloud Code Engine
[IBM Cloud Code Engine](https://cloud.ibm.com/docs/codeengine) is a fully managed, serverless platform that runs your containerized workloads. The Code Engine experience is designed so that you can focus on writing code and not on the infrastructure that is needed to host it. Code Engine can even build container images for you from your source code.

This tutorial will walk you through the steps to serve Watson NLP models on IBM Cloud Code Engine.

## Prerequisites
- Ensure you have an [IBM Cloud account](https://cloud.ibm.com/login)
- Install [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started)
- Install [Docker](https://docs.docker.com/get-docker/) 
- Ensure that Docker can access the [Watson NLP Runtime and pretrained model images](https://github.com/ibm-build-labs/Watson-NLP/blob/main/MLOps/access/README.md#docker).

**Tip**:
- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.


## Create the runtime container image

### Step 1: Download a couple of models to a local directory

<span style="font-size:x-small">

```
mkdir models
REGISTRY=cp.icr.io/cp/ai
MODELS="watson-nlp_syntax_izumo_lang_en_stock:0.0.4 watson-nlp_syntax_izumo_lang_fr_stock:0.0.4"
for i in $MODELS
do
  image=$REGISTRY/$i
  docker run -it --rm -e ACCEPT_LICENSE=true -v `pwd`/models:/app/models $image
done
```
</span>

### Step 2: Create a ```Dockerfile``` using a text editor of your choice

<span style="font-size:x-small">

```
ARG TAG=0.0.1
FROM cp.icr.io/cp/ai/watson-nlp-runtime:${TAG}
COPY models /app/models
```
</span>

### Step 3: Build the runtime image

<span style="font-size:x-small">

```
docker build -t my-watson-nlp-runtime:latest .
```
</span>


## Upload your runtime image to IBM Cloud Container Registry
Now the runtime image is created, let's put it on [IBM Cloud Container Registry (ICR)](https://cloud.ibm.com/docs/Registry), so that it can be used for deployment.

### Step 4: Install the Container Registry plug-in

<span style="font-size:x-small">

```
ibmcloud plugin install cr
```
</span>

### Step 5: Log in to your IBM Cloud account.

<span style="font-size:x-small">

```
ibmcloud login
```
</span>

Use `ibmcloud login --sso` command to login, if you have a federated ID.

### Step 6: Create a namespace
You'll need to create a [namespace](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#overview_elements_namespace) before you can upload your image, and make sure you're targeting the correct ICR [region](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#registry_regions).

Set a target region for the `ibmcloud cr` commands.

<span style="font-size:x-small">

```
ibmcloud cr region-set
```
</span>

Choose a name for your namespace, specified as `${NAMESPACE}`, and create the namespace.

<span style="font-size:x-small">

```
ibmcloud cr namespace-add ${NAMESPACE}
```
</span>

### Step 7: Login to ICR

<span style="font-size:x-small">

```
ibmcloud cr login
```
</span>

### Step 8: Upload the runtime image to ICR
Set `${REGISTRY}` to the listed Domain name for the [local registry regions](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#registry_regions_local) (or `icr.io` for the global registry), and run the following commands.
<span style="font-size:x-small">

```
# Tag the image
docker tag my-watson-nlp-runtime:latest ${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest

# Push the image
docker push ${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest
```
</span>


## Deploy the runtime to Code Engine
Once the runtime image is uploaded to ICR, we can use it to deploy a Code Engine application that serves Watson NLP models via a REST API.

### Step 9: Install the Code Engine plug-in.

<span style="font-size:x-small">

```
ibmcloud plugin install code-engine
```
</span>

### Step 10: Target a [region](https://cloud.ibm.com/docs/overview?topic=overview-locations) and a [reource group](https://cloud.ibm.com/docs/account?topic=account-rgs&interface=cli)

<span style="font-size:x-small">

```
ibmcloud target -r ${REGION} -g ${RESOURCE_GROUP}
```
</span>

### Step 11: Create a new [Code Engine project](https://cloud.ibm.com/docs/codeengine?topic=codeengine-manage-project)
In this example, a project named `my-ce-project` will be create in the region and resource group set by the previous command.

<span style="font-size:x-small">

```
ibmcloud ce project create --name my-ce-project
```
</span>

### Step 12: Select the project as the current context

<span style="font-size:x-small">

```
ibmcloud ce project select --name my-ce-project
```
</span>

### Step 13: Create a Code Engine managed secret from the IBM Cloud Web Console
If your applications in a project use an IBM Cloud Container Registry namespace that is in your account, you can let Code Engine create and manage the registry access secret for you to access the namespace from the project. The name of an automatically created registry access secret is of the format: `ce-auto-icr-private-${REGION}`, where `${REGION}` is the region, in which the namespace is created.

You can trigger a workflow to have a [Code Engine managed secret](https://cloud.ibm.com/docs/codeengine?topic=codeengine-add-registry#types-registryaccesssecrets) created for you as follows:
1. Open the [Code Engine console](https://cloud.ibm.com/codeengine/overview).
2. Select `Start creating` from `Run a container image`.
3. Select the project you created from the list of available projects.
4. Click `Configure image` next to the `Image reference` box.
5. Select the correct private ICR registry location for your namespace, such as `private.us.icr.io`.
6. Select `Code Engine managed secret` for Registry access secret.
7. Select the namespace you created.
8. Select the runtime image `my-watson-nlp-runtime` you uploaded.
9. Select the image tag `latest`.
10. Click `Done` at the bottom, and, because the image is in an ICR namespace in your account, Code Engine automatically creates the registry access secret for you.

You should be able to see the created registry access secret with the `ibmcloud ce registry list` command. With the registry access secret successfully created, you can now close the web console without actually creating an application, and move on to the next step.

### Step 14: Create an Code Engine application from the runtime image
At this point, you can simply create an application from your runtime image with a Code Engine CLI command.

<span style="font-size:x-small">

```
ibmcloud ce application create \
  --name watson-nlp-runtime \
  --port 8080 \
  --min-scale 1 --max-scale 2 \
  --cpu 2 --memory 4G \
  --image private.${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest \
  --registry-secret ce-auto-icr-private-${REGION}
```
</span>

It may take a few minutes to complete the deployment. If the deployment is successful, you'll get the URL of the application's public endpoint from the command output. Append `/swagger` to the URL and open it in a browser to access the Swagger UI, if you want to interact with the REST API resources provided by the Watson NLP Runtime.

### Step 15: Check your deployment
You can check the status of the application with the following commands:

<span style="font-size:x-small">

```
# List the applications
ibmcloud ce app list

# Check the application logs.
ibmcloud ce app logs --application watson-nlp-runtime

# Check the events
ibmcloud ce app events --application watson-nlp-runtime
```
</span>

### Step 16: Use curl to make a REST call
Once the Watson NLP Runtime service is ready, you should be able to send an inference request to the REST service endpoint as follows.

<span style="font-size:x-small">

```
curl -s -X POST "${PUBLIC_ENDPOINT}/v1/watson.runtime.nlp.v0/NlpService/SyntaxPredict" \
  -H "accept: application/json" \
  -H "grpc-metadata-mm-model-id: syntax_izumo_lang_en_stock" \
  -H "content-type: application/json" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ]}" \
  | jq -r .
```
</span>

**Tip**:
- The metadata value for `grpc-metadata-mm-model-id` should match the folder name of the model when it was downloaded and saved in `./models` in Step 2.

If you get a response like the following, the Watson NLP Runtime is working properly.

<span style="font-size:x-small">

```
{
  "text": "This is a test.",
  "producerId": {
    "name": "Izumo Text Processing",
    "version": "0.0.1"
  },
  "tokens": [
    {
      "span": {
        "begin": 0,
        "end": 4,
        "text": "This"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 5,
        "end": 7,
        "text": "is"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 8,
        "end": 9,
        "text": "a"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 10,
        "end": 14,
        "text": "test"
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    },
    {
      "span": {
        "begin": 14,
        "end": 15,
        "text": "."
      },
      "lemma": "",
      "partOfSpeech": "POS_UNSET",
      "dependency": null,
      "features": []
    }
  ],
  "sentences": [
    {
      "span": {
        "begin": 0,
        "end": 15,
        "text": "This is a test."
      }
    }
  ],
  "paragraphs": [
    {
      "span": {
        "begin": 0,
        "end": 15,
        "text": "This is a test."
      }
    }
  ]
}
```
</span>

## Clean up
Don't forget to clean up afterwards, to avoid paying for the cloud resources you no longer need.

Delete the application:

<span style="font-size:x-small">

```
ibmcloud ce app delete --name watson-nlp-runtime
```
</span>

Delete the project:

<span style="font-size:x-small">

```
ibmcloud ce project delete --name my-ce-project --hard
```
</span>

Note: If you do not specify the `--hard` option, the project can be restored within 7 days by using either the `project restore` or the `reclamation restore` command.

Delete the ICR namespace:

<span style="font-size:x-small">

```
ibmcloud cr namespace-rm ${NAMESPACE}
```
</span>

