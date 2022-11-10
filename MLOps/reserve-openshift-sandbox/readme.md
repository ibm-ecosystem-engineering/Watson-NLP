# Sandbox Environment

## Steps to Reserve an OpenShift Sandbox on IBM Cloud

### Step 1: Go to the TechZone Collection
Navigate with your browser to the following URL and log in to TechZone.
```
https://techzone.ibm.com/collection/watson-nlp-serving-models-with-standalone-containers
```

### Step 2: Go to the Journey 
Click on the tab `Run on Kubernetes or OpenShift`.

![Step 2](images/step2.png)

### Step 3: Request an Environment
Scroll down the page, look for `Sandbox Environment: Watson NLP Standalone Containers on IBM RedHat OpenShift Kubernetes Service (ROKS)` and click the reserve button.

![Step 3](images/step3.png)

### Step 4: Schedule the Reservation 
Choose either to `Reserve now` and `Schedule for later`.

![Step 4](images/step4.png)

### Step 5: Fill in the Reservation Form

![Step 5](images/step5.png)

### Step 6: Wait for your Environment
When the enviroment is ready, you will receive an email similar to the following.

![Step 6](images/step6.png)

Take note of the following information in the email.

- ***Integrated OpenShift container image registry***: The OpenShift internal `REGISTRY` that is provisioned with the environment.
- ***Project name***: The OpenShift namespace to be used, as well as the name of the internal container registry `NAMESPACE`.
- ***Project URL***: The path to log in to OpenShift cluster.

## Steps to login to OpenShift Cluster

Assuming that

- You have an [IBM Cloud account](https://cloud.ibm.com/login)
- You have installed [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started)

### Step 1: Log in to your IBM Cloud account

From the command terminal execute the below command

```
ibmcloud login
```

<sub>Use ibmcloud login --sso command to login, if you have a federated ID.</sub>

### Step 2: Go to the project URL in the email and login to your OpenShift cluster

![Step 7](images/step7.png)

### Step 3: Click on the top right corner on your Id, a drop down will be show and click on the `Copy login command'. A popup window will open

![Step 8](images/step8.png)

### Step 4: Click on the display token and copy the command 'Login in with this token` and execute in the terminal window

### Step 5: Login to OpenShift internal container registry

```
echo $(oc whoami -t) | docker login $REGISTRY -u $(oc whoami) --password-stdin
```

### Step 6: check status

```
oc get all
```
