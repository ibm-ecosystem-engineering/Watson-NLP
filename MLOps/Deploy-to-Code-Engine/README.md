# Serve Watson NLP Models with IBM Cloud Code Engine

[IBM Cloud Code Engine](https://cloud.ibm.com/docs/codeengine) is a fully managed, serverless platform that runs your containerized workloads. The Code Engine experience is designed so that you can focus on writing code and not on the infrastructure that is needed to host it. Code Engine can even build container images for you from your source code.

This tutorial will walk you through the steps to deploy a standalone Watson NLP Runtime to IBM Cloud Code Engine.

## Prerequisites

- Ensure you have your entitlement key to access the IBM Entitled Registry
- Ensure you have an [IBM Cloud account](https://cloud.ibm.com/login)
- Install [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started)
- Install [Docker](https://docs.docker.com/get-docker/)

**Tip**:

- [Podman](https://podman.io/getting-started/installation) provides a Docker-compatible command line front end. Unless otherwise noted, all the the Docker commands in this tutorial should work for Podman, if you simply alias the Docker CLI with `alias docker=podman` shell command.

## Create the runtime container image

The IBM Entitled Registry contains various container images for Watson Runtime. Once you've obtained the entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary), you can login to the registry with the key, and pull the runtime images to your local machine. The Watson Runtime on its own doesn't have any models included. However, you can easily build a runtime container image to include one or more pretrained models, which are also stored as container images in the IBM Entitled Registry.

### Step 1: Login to the IBM Entitled Registry

```sh
echo $IBM_ENTITLEMENT_KEY | docker login -u cp --password-stdin cp.icr.io
```

### Step 2: Download a couple of models to a local directory

Create a directory named `models`:

```sh
mkdir models
```

Set variable `REGISTRY` as follows to pull the images from IBM Entitled Registry.

```sh
REGISTRY=cp.icr.io/cp/ai
```

Use a variable `MODELS` to provide the list of models you want to download:

```sh
MODELS="watson-nlp_syntax_izumo_lang_en_stock:1.0.6 watson-nlp_syntax_izumo_lang_fr_stock:1.0.6"
```

Down the models into the local directory `models`:

```sh
for i in $(echo "$MODELS")
do
  image=${REGISTRY}/$i
  docker run -it --rm -e ACCEPT_LICENSE=true -v `pwd`/models:/app/models $image
done
```

### Step 3: Create a `Dockerfile` using a text editor of your choice

```dockerfile
ARG REGISTRY
ARG TAG=1.0.18
FROM ${REGISTRY}/watson-nlp-runtime:${TAG}
COPY models /app/models
```

### Step 4: Build the runtime image

```sh
docker build . -t my-watson-nlp-runtime:latest --build-arg REGISTRY=${REGISTRY}
```

## Upload your runtime image to IBM Cloud Container Registry

Now the runtime image is created, let's put it on [IBM Cloud Container Registry (ICR)](https://cloud.ibm.com/docs/Registry), so that it can be used for deployment.

### Step 5: Install the Container Registry plug-in

```sh
ibmcloud plugin install cr
```

### Step 6: Log in to your IBM Cloud account.

```sh
ibmcloud login
```

Use `ibmcloud login --sso` command to login, if you have a federated ID.

### Step 7: Create a namespace

You'll need to create a [namespace](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#overview_elements_namespace) before you can upload your image, and make sure you're targeting the correct ICR [region](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#registry_regions).

Set a target region for the `ibmcloud cr` commands.

```sh
ibmcloud cr region-set
```

Choose a name for your namespace, specified as `${NAMESPACE}`, and create the namespace.

```sh
ibmcloud cr namespace-add ${NAMESPACE}
```

### Step 8: Login to ICR

```sh
ibmcloud cr login
```

### Step 9: Upload the runtime image to ICR

Set variable `$REGISTRY` to the listed Domain name for the [local registry regions](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview#registry_regions_local) (or `icr.io` for the global registry), and run the following commands.

Tag the image:

```sh
docker tag my-watson-nlp-runtime:latest ${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest
```

Push the image:

```sh
docker push ${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest
```

## Deploy the runtime to Code Engine

Once the runtime image is uploaded to ICR, we can use it to deploy a Code Engine application that serves Watson NLP models via a REST API.

### Step 10: Install the Code Engine plug-in.

```sh
ibmcloud plugin install code-engine
```

### Step 11: Target a [region](https://cloud.ibm.com/docs/overview?topic=overview-locations) and a [reource group](https://cloud.ibm.com/docs/account?topic=account-rgs&interface=cli)

```sh
ibmcloud target -r ${REGION} -g ${RESOURCE_GROUP}
```

### Step 12: Create a new [Code Engine project](https://cloud.ibm.com/docs/codeengine?topic=codeengine-manage-project)

In this example, a project named `my-ce-project` will be create in the region and resource group set by the previous command.

```sh
ibmcloud ce project create --name my-ce-project
```

### Step 13: Select the project as the current context

```sh
ibmcloud ce project select --name my-ce-project
```

### Step 14: Create a Code Engine managed secret from the IBM Cloud Web Console

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

**Tip**:

- If you don't see a list of ICR registry locations or get error message, such as `Failed to create registry binding for 'IBM Registry Dallas'`, you may not have the required permissions to create a Code Engine managed secret. In that case, you can either ask the owner or Administrator of the IBM Cloud account for help, or create a registry access secret manually. See the [Code Engine documentation](https://cloud.ibm.com/docs/codeengine?topic=codeengine-add-registry) for more details.

With the registry access secret successfully created, you should be able to list it with the `ibmcloud ce registry list` command. Now close the web console without actually creating an application, and move on to the next step.

### Step 15: Create an Code Engine application from the runtime image

At this point, you can simply create an application from your runtime image with a Code Engine CLI command.

```sh
ibmcloud ce application create \
  --name watson-nlp-runtime \
  --port 8080 \
  --min-scale 1 --max-scale 2 \
  --cpu 2 --memory 4G \
  --image private.${REGISTRY}/${NAMESPACE}/my-watson-nlp-runtime:latest \
  --registry-secret ce-auto-icr-private-${REGION} \
  --env ACCEPT_LICENSE=true
```

It may take a few minutes to complete the deployment. If the deployment is successful, you'll get the URL of the application's public endpoint from the command output. Append `/swagger` to the URL and open it in a browser to access the Swagger UI, if you want to interact with the REST API resources provided by the Watson NLP Runtime.

### Step 16: Check your deployment

You can check the status of the application with the following commands.

List the applications:

```sh
ibmcloud ce app list
```

Check the application logs:

```sh
ibmcloud ce app logs --application watson-nlp-runtime
```

Check the events:

```sh
ibmcloud ce app events --application watson-nlp-runtime
```

### Step 17: Use curl to make a REST call

Once the Watson NLP Runtime service is ready, you should be able to send an inference request to the REST service endpoint as follows.

```sh
curl -s -X POST "${PUBLIC_ENDPOINT}/v1/watson.runtime.nlp.v1/NlpService/SyntaxPredict" \
  -H "accept: application/json" \
  -H "grpc-metadata-mm-model-id: syntax_izumo_lang_en_stock" \
  -H "content-type: application/json" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ]}" \
  | jq -r .
```

**Tip**:

- The metadata value for `grpc-metadata-mm-model-id` should match the folder name of the model when it was downloaded and saved in `./models` in Step 2.

If you get a response like the following, the Watson NLP Runtime is working properly.

```json
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

## Clean up

Don't forget to clean up afterwards, to avoid paying for the cloud resources you no longer need.

Delete the application:

```sh
ibmcloud ce app delete --name watson-nlp-runtime
```

Delete the project:

```sh
ibmcloud ce project delete --name my-ce-project --hard
```

Note: If you do not specify the `--hard` option, the project can be restored within 7 days by using either the `project restore` or the `reclamation restore` command.

Delete the ICR namespace:

```sh
ibmcloud cr namespace-rm ${NAMESPACE}
```
