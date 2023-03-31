# Deploy Watson NLP in AWS ECS Cluster

With IBM Watson NLP, IBM introduced a common library for natural language processing, document understanding, translation, and trust. IBM Watson NLP brings everything under one umbrella for consistency and ease of development and deployment. This tutorial walks you through the steps to build a container image to serve pretrained Watson NLP models and to run it with Docker. The container image includes both the Watson NLP Runtime and the models. When the container runs, it exposes REST and gRPC endpoints that client programs can use to make inference requests on the models.

Amazon Elastic Container Service (ECS) is a fully managed container orchestration service that helps you easily deploy, manage, and scale containerized applications that supports Docker containers and allows you to run applications on a managed cluster of Amazon Elastic Compute Cloud (Amazon EC2) instances and Fargate.

This tutorial you are going to deploy a pretrained models `watson-nlp_syntax_izumo_lang_en_stock:1.0.6` but other pretrained models also can be served.

## Prerequisite

- Ensure you have your entitlement key to access the IBM Entitled Registry to access [Watson NLP Runtime and pretrained models](https://github.com/ibm-build-lab/Watson-NLP/blob/main/MLOps/access/README.md#kubernetes-and-openshift)
- Ensure you have an AWS account
- [Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) AWS CLI

**Tip**:

- If you don't have an AWS account, you may want to consider [AWS Free Tier](https://aws.amazon.com/free/free-tier/).
- Follow the [security best practices](https://docs.aws.amazon.com/accounts/latest/reference/best-practices-root-user.html) for the root user of your AWS account, and [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html) for daily use.
- Make sure you have [required permissions](https://docs.docker.com/cloud/ecs-integration/#requirements) on AWS account to run applications on ECS.

## Create Watson NLP container image

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
MODELS="watson-nlp_syntax_izumo_lang_en_stock:1.0.6"
```

Copy the models into the local directory `models`:

```sh
for i in $MODELS
do
  image=${REGISTRY}/$i
  docker run -it --rm -e ACCEPT_LICENSE=true -v `pwd`/models:/app/models $image
done
```

### Step 3: Create a `Dockerfile` using a text editor of your choice

```sh
ARG REGISTRY
ARG TAG=1.0.18
FROM ${REGISTRY}/watson-nlp-runtime:${TAG}
COPY models /app/models
```

### Step 4: Build the image

```sh
docker build . -t my-watson-nlp-runtime:latest --build-arg REGISTRY=${REGISTRY}
```

## Upload your runtime image to Amazon ECR

Now the runtime image is created, let's put it on [Amazon ECR](https://aws.amazon.com/ecr/), so that it can be used for deployment. Each AWS account is provided with a [default private registry](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html) (*aws_account_id*.dkr.ecr.*region*.amazonaws.com).

### Step 5: Login to the default registry

Set an environment variable for the default private registry as appropriate:

```sh
export DEFAULT_REGISTRY=<your-12-digit-account-id>.dkr.ecr.<region>.amazonaws.com
```

Login to the default private registry:

```sh
aws ecr get-login-password | docker login --username AWS --password-stdin ${DEFAULT_REGISTRY}
```

### Step 6: Create a repository in the default registry

```sh
aws ecr create-repository --repository-name my-watson-nlp-runtime
```

### Step 7: Upload the image to Amazon ECR

```sh
docker tag my-watson-nlp-runtime:latest ${DEFAULT_REGISTRY}/my-watson-nlp-runtime:latest
```

Push the image:

```sh
docker push ${DEFAULT_REGISTRY}/my-watson-nlp-runtime:latest
```

## Deploy the Runtime to Amazon ECS

Set the cluster name in an environment variable.

```sh
CLUSTER_NAME=MyFargateCluster
```

## Create secret to pull watsn nlp images

Create a new file name `task-definition.json` and save the following content. Please change the `image:` location where you pushed the image in the previous step. And also `executionRoleArn:` 

```json
{
    "family": "ecs-watson-nlp-app", 
    "networkMode": "awsvpc", 
    "containerDefinitions": [
        {
            "name": "watson-nlp-app", 
            "image": "us.icr.io/watson-core-demo/watson-nlp-demo:v1", 
            "repositoryCredentials": {
                "credentialsParameter": "arn:aws:secretsmanager:us-east-2:481118440516:secret:watsonlib-ibmecs-nXztkK"
            },
            "portMappings": [
                {
                    "containerPort": 8080, 
                    "hostPort": 8080, 
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "ACCEPT_LICENSE",
                    "value": "true"
                }
            ]
        }
    ], 
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "memory": "6 GB",
    "cpu": "1024",
    "executionRoleArn": "arn:aws:iam::481118440516:role/ecsTaskExecutionRole" 
}
```

### Step 8: Register the task definition

```sh
TASK_FAMILY=watson-nlp-runtime
```

```sh
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

Check if the task definition registered successfully.

```sh
aws ecs list-task-definitions
```

output:

```json
{
    "taskDefinitionArns": [
        "arn:aws:ecs:us-east-2:507003332374:task-definition/watson-nlp-runtime:1"
    ]
}
```

To view the task-defintion execute the below command.

```sh
aws ecs describe-task-definition --task-definition "$TASK_FAMILY" --region "us-east-2"
```

### Step 9: The Watson NLP ECS Services

execute the below command and create ECS service passing the task defintion.

```sh
aws ecs create-service \
--cluster $CLUSTER_NAME \
--service-name watson-nlp-svc \
--task-definition watson-nlp-runtime:1 \
--desired-count 1 \
--launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0906c6ef826ea3898, subnet-0cad8624ef5e2d544, subnet-0a595854bb4af7860],securityGroups=[sg-00cd1568797e76974],assignPublicIp=ENABLED}"
```

It will take some time to deploy the NLP model. To see list of services

```sh
aws ecs list-services --cluster $CLUSTER_NAME
```

```sh
aws ecs describe-services --cluster $CLUSTER_NAME --services watson-nlp-svc
```

```sh
aws ecs run-task --cluster $CLUSTER_NAME --task-definition watson-nlp-runtime:1 --count 1 --network-configuration "awsvpcConfiguration={subnets=[subnet-0906c6ef826ea3898, subnet-0cad8624ef5e2d544, subnet-0a595854bb4af7860],securityGroups=[sg-00cd1568797e76974],assignPublicIp=ENABLED}" --launch-type FARGATE 
 ```


```sh
aws ecs list-services --cluster fargate-cluster --cluster fargate-watsonlib-ecs
```

```sh
aws ecs describe-services --services ecs-watson-nlp --cluster fargate-watsonlib-ecs
```

