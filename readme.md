# Self-Serve Assets for Embeddable AI using Watson NLP

[Assets/Accelerators for Watson NLP](https://github.com/ibm-build-labs/Watson-NLP) (this repo) contains self-serve notebooks and documentation on how to create NLP models using Watson NLP library, how to serve Watson NLP models, and how to make inference requests from custom applications. With an IBM Cloud account a full production sample can be deployed in roughly one hour.

Key Technologies:

- [IBM Watson NLP](https://ibmdocs-test.mybluemix.net/docs/en/watson-libraries?topic=watson-natural-language-processing-home) (Natural Language Processing) comes with a wide variety of text processing capabilities, such as emotion analysis and topic modeling. Watson NLP is built on top of the best AI open source software. It provides stable and supported interfaces, it handles a wide range of languages and its quality is enterprise proven. The Watson NLP containers can be deployed with Docker, on various Kubernetes-based platforms, or using cloud-based container services.

## Outline

Machine Learning notebooks, tutorials, and datasets focused on supporting a Data Science Engineer are under the [ML folder](ML/). Assets focused on deployment are under the [MLOps folder](MLOps/). Go to the respective folders to learn more about these assets.

- [ML Assets](ML/)
  - [Emotion Classification](ML/Emotion-Classification/)
    - [Emotion Classification Tutorial](ML/Emotion-Classification/Emotion%20Classification%20Tutorial.md)
    - [Emotion Classification Pre-trained Notebook](ML/Emotion-Classification/Emotion%20Classification%20-%20Pre-Trained%20Models.ipynb)
    - [Emotion Classification Custom Training Notebook](ML/Emotion-Classification/Emotion%20Classification%20-%20Custom%20Model%20Training.ipynb)
    - [Emotion Classification Dataset](ML/Emotion-Classification/emotion-tweets.csv)
  - [Entities & Keywords Extraction](ML/Emotion-Classification/)
    - [Entities, Keywords & Phrases Extraction Tutorial](ML/Entities-Keywords-Extraction/Entities-extraction-Tutorial.md)
    - [Entities, Keywords & Phrases Extraction Notebook](ML/Entities-Keywords-Extraction/Hotel%20Reviews%20Analysis%20-%20Entities%20and%20Keywords.ipynb)
    - [Belgrave Hotel Dataset](ML/Entities-Keywords-Extraction/uk_england_london_belgrave_hotel.csv)
    - [Dorset Hotel Dataset](ML/Entities-Keywords-Extraction/uk_england_london_dorset_square.csv)
    - [Euston Hotel Dataset](ML/Entities-Keywords-Extraction/uk_england_london_euston_square_hotel.csv)
  - [Sentiment Analysis](ML/Sentiment-Analysis/)
    - [Sentiment Analysis Tutorial](ML/Sentiment-Analysis/Sentiment%20Analysis%20Tutorial%20extended.md)
    - [Sentiment Analysis Pre-trained Notebook](ML/Sentiment-Analysis/Sentiment%20Analysis%20-%20Pre-Trained%20models.ipynb)
    - [Sentiment Analysis Fine-tune/Re-training Notebook](ML/Sentiment-Analysis/Sentiment%20Analysis%20-%20Model%20Training.ipynb)
    - [Sentiment Analysis Dataset](ML/Sentiment-Analysis/movies_small.csv)
  - [Text Classification](ML/Text-Classification)
    - [Text Classification Tutorial](ML/Text-Classification/Text-Classification-Tutorial.md)
    - [Consumer Complaint Text Classification Notebook](ML/Text-Classification/Consumer%20complaints%20Classification.ipynb)
    - [Hotel Reviews Text Classification](ML/Text-Classification/Hotel%20Reviews%20Classification.ipynb)
  - [Topic Modeling](ML/Topic-Modeling)
    - [Topic Modeling Tutorial](ML/Topic-Modeling/Topic-Modeling-Tutorial.md)
    - [Topic Modeling Notebook](ML/Topic-Modeling/Complaint%20Data%20Topic%20Modeling.ipynb)
    - [Topic Modeling Comparison with LDA Notebook](ML/Topic-Modeling/Complaint%20Data%20Topic%20Modeling%20-%20Compare%20With%20LDA.ipynb)
- [MLOps Assets](MLOps/)
  - [Serve Pretrained Models using Docker](MLOps/Watson-NLP-Container)
  - [Serve Custom Models using Docker](MLOps/Watson-NLP-Custom-Model-Container)
  - [Serve Models with Standalone Containers on Kubernetes or OpenShift](MLOps/Watson-NLP-Container-k8)
  - [Serve Models with AWS Fargate](MLOps/Deploy-to-AWS-Fargate)
  - [Serve Models with Azure Container Instances](MLOps/Deploy-to-Azure-Container-Instances)
  - [Serve Models with IBM Code Engine](MLOps/Deploy-to-Code-Engine)
  - [Serve Pretrained Models on Kubernetes or OpenShift](MLOps/Init-Container)
  - [Serve Custom Models with Kubernetes or OpenShift](MLOps/custom-model-k8s)
  - [Serve Models with KServe ModelMesh](MLOps/Deploy-to-KServe-ModelMesh-Serving)
  - [Create an NLP Python Client](MLOps/Dash-App-gRPC-Client)

## Resources

- IBM Watson NLP Library for Embed
  - [Software Announcement](https://www.ibm.com/common/ssi/ShowDoc.wss?docURL=/common/ssi/rep_ca/1/897/ENUS222-291/index.html&lang=en&request_locale=en)
  - [Documentation](https://www.ibm.com/docs/en/watson-libraries?topic=watson-natural-language-processing-library-embed-home)
- IBM Technology Zone assets
  - [Embeddable AI](https://techzone.ibm.com/collection/embedded-ai)
  - [Watson NLP - Text Classification](https://techzone.ibm.com/collection/watson-nlp-text-classification)
  - [Watson NLP - Entities & Keywords extraction](https://techzone.ibm.com/collection/watson-nlp-entities-keywords-extraction)
  - [Watson NLP - Topic Modeling](https://techzone.ibm.com/collection/watson-nlp-topic-modeling)
  - [Watson NLP - Sentiment and Emotion Analysis](https://techzone.ibm.com/collection/watson-core-nlp)
  - [Watson NLP - Creating Client Applications](https://techzone.ibm.com/collection/watson-nlp-creating-client-applications)
  - [Watson NLP - Serving Models with Standalone Containers](https://techzone.ibm.com/collection/watson-nlp-serving-models-with-standalone-containers)
  - [Watson NLP - Serving Models with Kubernetes and OpenShift](https://techzone.ibm.com/collection/watson-nlp-serving-nlp-models)
- IBM Developer Tutorials
  - [Embeddable AI Homepage](https://developer.ibm.com/technologies/embeddable-ai/)
  - [Set up your Watson NLP Environment](https://developer.ibm.com/tutorials/set-up-your-ibm-watson-libraries-environment/)
  - [Use the Watson NLP Library to Perform Emotion Classification](https://developer.ibm.com/tutorials/use-the-watson-nlp-library-to-perform-emotion-classification/)
  - [Use the Watson NLP Library to Perform Sentiment Analysis](https://developer.ibm.com/tutorials/use-the-watson-core-nlp-library-to-perform-sentiment-analysis/)
