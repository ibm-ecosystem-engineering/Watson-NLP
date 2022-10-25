# Serve Watson NLP Models with Azure Container Instances
[Azure Container Instances (ACI)](https://aws.amazon.com/) offers the fastest and simplest way to run a container in Azure, without having to manage any virtual machines and without having to adopt a higher-level service.

This tutorial will walk you through the steps to deploy a standalone Watson NLP Runtime to Azure Container Instances.

## Prerequisites
- Ensure you have your entitlement key to access the IBM Entitled Registry
- Ensure you have an Azure account
- [Install](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) Azure CLI
- Download and install the latest version of [Docker Desktop](https://docs.docker.com/desktop/)
  - [Download for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Download for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - Alternatively, install the [Docker Compose CLI for Linux](https://docs.docker.com/cloud/ecs-integration/#install-the-docker-compose-cli-on-linux)

**Tip**:
- If you don't have an Azure account, you may want to consider [Azure free account](https://azure.microsoft.com/en-us/free/).

## Upload some Watson NLP container images to Azure Container Registry
[Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/) (ACR) is a private registry service for building, storing, and managing container images and related artifacts. IBM Entitled Registry contains various container images for Watson Runtime and associated pretrained models. Once you've obtained the entitlement key from the [container software library](https://myibm.ibm.com/products-services/containerlibrary), you can login to the registry with the key, and pull the container images to your local machine. Then you can push those images into an ACR registry in the same region you'd deploy the runtime, to achieve better performance and reliability in your deployment.

### Step 1: Login to the IBM Entitled Registry

<span style="font-size:x-small">

```
echo $IBM_ENTITLEMENT_KEY | docker login -u cp --password-stdin cp.icr.io
```
</span>

### Step 2: Login to your Azure account
The Azure CLI's [default authentication method](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli#sign-in-interactively) for logins uses a web browser and access token to sign in.

<span style="font-size:x-small">

```
az login
```
</span>

### Step 3: Create a resource group
An Azure [resource group](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-cli#what-is-a-resource-group) is a logical container into which Azure resources are deployed and managed. To create a resource group, use the `az group create` command.

<span style="font-size:x-small">

```
az group create --name $RG --location $REGION
```
</span>

**Tip**:
- You can list the supported [regions](https://learn.microsoft.com/en-us/azure/availability-zones/az-overview) for the current [subscription](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/decision-guides/subscriptions/) with the `az account list-locations --output table` command.

### Step 4: Create a registry in ACR
You can create an ACR instance using the `az acr create` command.

<span style="font-size:x-small">

```
az acr create \
  --name $REGISTRY \
  --resource-group $RG \
  --sku Basic \
  --location $REGION
```
</span>

### Step 5: Login to the ACR registry
When you log in with `az acr login`, the CLI uses the token created when you executed `az login` to seamlessly authenticate your session with your registry. The token used by `az acr login` is valid for 3 hours. If your token expires, you can refresh it by using the `az acr login` command again to reauthenticate.

<span style="font-size:x-small">

```
az acr login --name $REGISTRY
```
</span>

### Step 6: Copy container images to ACR
You can now copy the container images of a Watson NLP Runtime and some pretrained models from IBM Entitled Registry to the ACR registry you just created. 

Set the source registry:
<span style="font-size:x-small">

```
REGISTRY1=cp.icr.io/cp/ai
```
</span>

Set the destination registry:
<span style="font-size:x-small">

```
REGISTRY2=${REGISTRY}.azurecr.io
```
</span>

Specify the container images you need:
<span style="font-size:x-small">

```
IMAGES="watson-nlp-runtime:1.0.18 watson-nlp_syntax_izumo_lang_en_stock:1.0.6"
```
</span>

Copy the container images:
<span style="font-size:x-small">

```
for i in $IMAGES
do
  image1=${REGISTRY1}/$i
  image2=${REGISTRY2}/$i
  docker pull $image1
  docker tag $image1 $image2
  docker push $image2
done
```
</span>


## Deploy the Runtime to ACI
The [Docker Azure Integration](https://docs.docker.com/cloud/aci-integration/) enables developers to use native Docker commands to run applications in Azure Container Instances (ACI) when building cloud-native applications. The new experience provides a tight integration between Docker Desktop and Microsoft Azure allowing developers to quickly run applications using the Docker CLI or VS Code extension, to switch seamlessly from local development to cloud deployment.

### Step 7: Create an ACI context in Docker
Run the `docker context create` command to create an ACI Docker context named `myacicontext`.

<span style="font-size:x-small">

```
docker context create aci myacicontext \
  --resource-group $RG \
  --location $REGION
```
</span>

### Step 8: Create a Compose file
The [Compose file](https://docs.docker.com/compose/compose-file/) is a YAML file defining services, networks, and volumes for a Docker application. The default path for a Compose file is `compose.yaml` (preferred) or `compose.yml` in the working directory.

<span style="font-size:x-small">

```
version: "3.8"

services:
  runtime:
    image: ${REGISTRY}.azurecr.io/watson-nlp-runtime:1.0.18
    environment:
      - ACCEPT_LICENSE=true
    domainname: $DOMAIN
    ports:
      - target: 8080
    volumes:
    - models:/app/models
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4096M

networks:
  default:

volumes:
  models:
    driver: azure_file
    driver_opts:
      share_name: models
      storage_account_name: $STORAGEACCOUNT
```
</span>

**Note**:
- You can optionally expose the runtime service on an FQDN of the form: `${DOMAIN}.${REGION}.azurecontainer.io`, with the `domainname: $DOMAIN` field in the Compose file.
- If a [Azure storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview) named `$STORAGEACCOUNT` and an NFS share in [Azure Files](https://learn.microsoft.com/en-us/azure/storage/files/) named `models` in the storage account don't already exist, they would be created automatically.

### Step 9: Deploy it to ACI
Run the `docker compose up` command to deploy it as a project named `myproject`.

<span style="font-size:x-small">

```
docker --context myacicontext compose --project-name myproject up
```
</span>

### Step 10: Check your deployment
It may take a few minutes to complete the deployment. If successfully deployed, the service can be listed with the `docker ps` command, which shows the `hostname:port` you need for accessing the service endpoint of the deployed Watson NLP Runtime. Append `/swagger` to the URL and open it in a browser to access the Swagger UI, if you want to interact with the REST API resources provided by the Watson NLP Runtime.

<span style="font-size:x-small">

```
docker --context myacicontext ps
```
</span>

You can also check the runtime container's logs with the `docker logs` command.

<span style="font-size:x-small">

```
docker --context myacicontext logs myproject_runtime
```
</span>

### Step 11: Copy a pretrained model into the storage volume
The Watson Runtime on its own doesn't have any models included. You need to copy the pretrained model in the model image you've uploaded to ACR into the NFS share `models`, which is mounted on the runtime container as a storage volume. This can be achieved by running another container with the model image as follows.

<span style="font-size:x-small">

```
docker --context myacicontext run \
  --name model1 \
  -v ${STORAGEACCOUNT}/models:/app/models \
  -e ACCEPT_LICENSE=true \
  ${REGISTRY}.azurecr.io/watson-nlp_syntax_izumo_lang_en_stock:1.0.6
```
</span>

### Step 12: Restart the deployed runtime container to load the model from the storage volume

Stop the runtime container:
<span style="font-size:x-small">

```
docker --context myacicontext stop myproject
```
</span>

Start the runtime container:
<span style="font-size:x-small">

```
docker --context myacicontext start myproject
```
</span>

### Step 13: Use curl to make a REST call
Once the Watson NLP Runtime service is ready again with the pretrained model successfully loaded, you should be able to send an inference request to the REST service endpoint as follows.

<span style="font-size:x-small">

```
curl -s -X POST "http://${DOMAIN}.${REGION}.azurecontainer.io:8080/v1/watson.runtime.nlp.v1/NlpService/SyntaxPredict" \
  -H "accept: application/json" \
  -H "grpc-metadata-mm-model-id: syntax_izumo_lang_en_stock" \
  -H "content-type: application/json" \
  -d "{ \"rawDocument\": { \"text\": \"This is a test.\" }, \"parsers\": [ \"TOKEN\" ]}" \
  | jq -r .
```
</span>

**Tip**:
- The value of metadata `grpc-metadata-mm-model-id` should match the folder name of the model in the Azure Files storage.

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
Don't forget to clean up afterwards with the `docker compose down` command, to avoid paying for the cloud resources you no longer need.

<span style="font-size:x-small">

```
docker --context myacicontext compose --project-name myproject down
```
</span>


To delete the `model1` container, run the `docker rm` command.

<span style="font-size:x-small">

```
docker --context myacicontext rm model1
```
</span>

To delete the NFS share, run the `docker volume rm` command as follows.

<span style="font-size:x-small">

```
docker --context myacicontext volume rm ${STORAGEACCOUNT}/models
```
</span>

