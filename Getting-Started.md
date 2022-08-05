## Getting Started with Watson NLP on TechZone

This guide will show you how to set up a Python notebook environment using Watson Studio on IBM Cloud so that you can use the Watson NLP library.  This guide demonstrates how to set things up for the Sentiment Analysis tutorial.  The flow for Emotion Classification is similar.

### Steps:
#### Reserve your env
1. Under the [Sentiment Analysis](https://techzone.ibm.com/collection/watson-core-nlp#tab-1) tab, find the environment tile and click **Reserve** to reserve a Watson Studio environment.

![reserve](Screenshots/reserve.png)

2. Shortly, you will receive an email inviting you to join an IBM cloud account. Follow the instructions in the email to join.  Your environment should be ready within a few minutes.  When it is ready, you will recieve a second email similar to the following.

![env_details](Screenshots/env_details.png)

3. Log in to [IBM Cloud Pak for Data](https://dataplatform.cloud.ibm.com). Once logged in, ensure that you are using cloud account **2577353 - tsglwatson**. You can check the name of the current account in the bar the top of the screen.  Change the account if necessary using the drop-down menu.  From the IBM Cloud Pak for Data dashboad, find the tile for the Project that you want to work with.  For the Sentiment Analysis tutorial, the name of this Project will have the prefix **sentiment-analysis**.  Once the Project is open, you can view the notebooks and data assets of the project using the **Assets** tab.

![assets](Screenshots/assets.png)

4. Before working with the notebooks, you need to define the environment in which these notebooks will run. To get started on that, click on the **Manage** tab.

![manage_tab](Screenshots/manage_tab.png)

5. Click on **Environments** from the side Navbar. Next click on **Templates** tab. Finally, click on **New template**

![env](Screenshots/env.png)

6. We will create an environment template that contains the Watson NLP library. Give your environment template a name like **Watson NLP**. In the Hardware configuration, select at least **4 vCPU and 16 GB RAM**. For Software, select **Default Python 3.8 + Watson NLP(beta)**. Finally click **Create**

![new_env_settings](Screenshots/new_env_settings.png)

7. Now we will set an environment for a notebook.  Click on the **Assets** tab. Find the notebook you want to work with among the assets.  Click on the ellipsis (the three dots) to the right of the notebook name in order to open a drop-down menu.  Within this menu click **Change environment**.

![change_env](Screenshots/change_env.png)

8. Select the environment template that you created previously and click **Change**.
 
![change](Screenshots/change.png)

9. You will be able to run the notebook by clicking the ellipsis and selecting **Edit**.

![edit](Screenshots/edit.png)

10. Your notebook will load and you can follow the instructions in your notebook to complete the tutorials on Watson NLP.

![loaded](Screenshots/loaded.png)
