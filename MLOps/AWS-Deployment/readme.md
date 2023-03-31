# IBM Watson Libraries AWS Deployment guide

Get started quickly using IBM Watson Libraries with this list of assets to deploy in AWS platform.

With Watson Libraries, IBM introduced a common library framework for natural language processing (NLP), speech, document understanding, translation, and trust. It's a framework that is specifically designed for developers to embed AI into their products. IBM Watson Libraries is designed to help lower the barrier for AI adoption by helping address the skills shortage and development costs that are required to build AI models from scratch.

The three libraries available are:

- [IBM Watson Natural Language Processing library:](https://www.ibm.com/products/ibm-watson-natural-language-processing) This library is designed to help you provide capabilities to process human language to derive meaning and context.
- [IBM Watson Speech to Text library:](https://www.ibm.com/products/watson-speech-embed-libraries) This library is designed to enable speech transcription with speed and accuracy to help businesses improve customer service experiences.
- [IBM Watson Text to Speech library:](https://www.ibm.com/products/watson-speech-embed-libraries) This library is designed to enable you to convert written text into natural sounding audio with accuracy in various languages and voices.

The libraries include innovations that are developed by IBM Research as well as open source technology and are designed to reduce the time and resources that are required for a developer to add powerful AI to an application.

The Watson NLP library comes with hundreds of pretrained models in a vast assortment of global languages with dozens of modules for NLP tasks, including sentiment analysis, phrase extraction, and text classification. Using these models, you can save time and compute costs on training models and return the value of embedded AI faster.

To help you get started in AWS platform quickly using IBM Watson Libraries, Follow the following tutorials for Watson NLP and Speech library.


## Deploy on Redhat OpenShift AWS (ROSA) and EKS EC2/Fargate

- Deploy IBM Watson Natural Language Processing library:
  - [Init container approach](https://developer.ibm.com/tutorials/serve-pretrained-models-on-kubernetes-or-openshift/) An IBM developer tutorial on how to deploy Watson NLP Models with Init-Container approach. In this approach you can directly access all pre-trained model from your deployment. You don't have to build the container and push it in a private repository
  - [build container and store in private repository](https://developer.ibm.com/tutorials/serve-models-on-kubernetes-using-standalone-containers/) This approach you build container in your machine, push the image in a private repository and deploy NLP container.
- Deploy IBM Watson Speech to Text library: The STT service can be deployed either with or without customization. A customizable deployment allows users to update the service to understand how to transcribe words.
  - [STT runtime only](https://github.com/ibm-build-lab/Watson-Speech/tree/main/stt-runtime-openshift)
  - [Customization deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/stt-customization-openshift)
- IBM Watson Text to Speech library deployment: The TTS service also can be deployed either with or without customization.
  - [TTS runtime only](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-runtime-openshift)
  - [Customization deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-customization-openshift)
  
 ## Deploy on ECS Fargate
 
 - [Deploy IBM Watson Natural Language Processing library](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/Deploy-to-AWS-Fargate)
