# Tutorial for Elytra NLP Rules Editor

This tutorial explains the basic concepts in the NLP editor for generating the custom rules for detecting Driving License Number.

# Setup the Elyra Visual NLP Editor using Docker container.

You will find below instructions for running the NLP Editor frontend and the AQL processing SystemT backend together inside an all-in-one docker container.

## Prerequsites:

* Docker 
* All-in-one docker container [Download](https://ibm.box.com/s/sw901pmlq27i0bqkb7aaiejolcgflt8q) 
* Please request download access of all-in-one container on slack channel <b>#nlp_rules_visual_editor_canvas</b>


1. Follow steps below to **Run the editor locally**


2. Extract `01-ibm_watson_discovery_nlp_web_tool_frontend_backend-<date>.tar.gz` into a folder of your choice, say `watson_nlp_web_tool`

3. Build the container image
   ```
   cd watson_nlp_web_tool
   docker build -t watson_nlp_web_tool:1.0 
   ``` 

4. Run the container image with volumes mapped.

   ```
   docker run -d -p 8080:8080 --name watson_nlp_web_tool watson_nlp_web_tool:1.0
   ```

5. Open http://localhost:8080 in a web browser. 

![step1](Screenshots/Elyra%20doc%20step1.png)


# Generate the custom rules for Driving License Number 

## 1. Set up the input document
Expand the Extractors, drag and drop Input Documents on the canvas. Configure with document [Driving License Data](https://github.com/ibm-build-lab/Watson-NLP/blob/main/ML/PII-Extraction/PII_faker_LicenseNumber_sentances.txt). Click Upload, then Close.

![step2](Screenshots/Elyra%20doc%20step2.png)

## 2. Create a dictionary of Driving License Keywords

Under **Extractors**, drag **Dictionary** on the canvas. Connect its input to the output of **Input Documents**. 
Rename the node to `DLicence` and enter the terms: `Driving` and `Licence`, check the IGNORE CASE option BELOW. Click **Save**.
(Skip the test if you want to detect direct Driving Licence number without any context)

![step3](Screenshots/Elyra%20doc%20step3.png)

## 3. Run the dictionary and see results highlighted

Select the `DLicence` node, and click **Run**.

![step4](Screenshots/Elyra%20doc%20step4.png)

## 4. Create a regular expression to capture Driving Licence Number 

In the United States, the driver's license number pattern varies across states, with each state having its own unique set of regulations and formats for assigning the license numbers, this demonstration includes 10 United State's regular expression for captures Driving Licence Number.


|State|Driving License Pattern|
|-----|-----------------------|
|California,Texas & Hawaii| [a-zA-Z]{1}[0-9]{8}|
|Arkansas & South Carolina|[0-9]{9}|
|Alaska & Alabama|[0-9]{7}|
|North Carolina|[0-9]{12}|
|Colorado|[0-9]{2}(-)[0-9]{3}(-)[0-9]{4}|
|New York|[0-9]{3}(-)[0-9]{3}(-)[0-9]{3}|

Combined regular expression: `\b[a-zA-Z]{1}[0-9]{8}(\b)|\b[0-9]{9}($|\b)|\b[0-9]{7}($|\b)|[0-9]{12}($|\b)|[0-9]{2}(-| |)[0-9]{3}(-| |)[0-9]{4}|[0-9]{3}(-| |)[0-9]{3}(-| |)[0-9]{3}`


Under Extractors, drag RegEx to the canvas. Name it `Driving_Licence_Number` and specify the regular expression as explain above. Click Save, then Run. The regular expression captures mentions of Driving Licence Number.

![step5](Screenshots/Elyra%20doc%20step5.png)

![step6](Screenshots/Elyra%20doc%20step6.png)

## 5. Create a sequence to combine the Driving Licence key words and Driving License Number 

Create a sequence called `Driving_Licence_Detect` and specify the pattern as `(<DLicence .DLicence >)<Token>{1,2}(<Driving_Licence_Number.Driving_Licence_Number>)`, Click **Save** and **Run**.

![step7](Screenshots/Elyra%20doc%20step7.png)

This step helps to identify Driving Licence Number with Keywords. If you want to detect only Driving Licence Number without Keywords then skip the step3 and step5 and directly prepare Regex patterns as shown in step4.


## 6. Consolidate the final Driving Licence Number detection

If you notice the result of step 5, it can not detect Driving Licence Number if Keyword are after the numbers. We can add Consolidate canvas for resolving this issue. Under Refinement, drag Consolidate on the canvas and connect its input with Driving_Licence_Detect. Rename it to Driving_Licence_Consolidated Click Save.


![step8](Screenshots/Elyra%20doc%20step8.png)

Select the `Driving_Licence_Consolidated` node, and click Run.


![step9](Screenshots/Elyra%20doc%20step9.png)

The above result detect all the available Driving Licence Numbers in the document. So now select the final `Driving_Licence_Consolidated` canvas and click on the export button. It will generate the `NLP_Canvas_Export.zip` file for the custom rules to detect the Driving Licencee Number. This exported zip file will be used in [`PII Extraction - Custom-RBR Models Notebook`](https://github.com/ibm-build-lab/Watson-NLP/blob/main/ML/PII-Extraction/PII%20Extraction%20-%20Custom-RBR%20Models.ipynb) to create a custom rule based model in the Watson NLP library.
