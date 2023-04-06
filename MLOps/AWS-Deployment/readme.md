# IBM Watson Libraries AWS Deployment Cheatsheet

This cheatsheet points you to tutorials you can use to deploy Watson Libraries on AWS.

With Watson Libraries, IBM introduced a common library framework for natural language processing (NLP), speech, document understanding, translation, and trust. It's a framework that is specifically designed for developers to embed AI into their products. IBM Watson Libraries is designed to help lower the barrier for AI adoption by helping address the skills shortage and development costs that are required to build AI models from scratch.

The three libraries available are:

- [IBM Watson Natural Language Processing library:](https://www.ibm.com/products/ibm-watson-natural-language-processing) This library is designed to help you provide capabilities to process human language to derive meaning and context.
- [IBM Watson Speech to Text library:](https://www.ibm.com/products/watson-speech-embed-libraries) This library is designed to enable speech transcription with speed and accuracy to help businesses improve customer service experiences.
- [IBM Watson Text to Speech library:](https://www.ibm.com/products/watson-speech-embed-libraries) This library is designed to enable you to convert written text into natural sounding audio with accuracy in various languages and voices.

The libraries include innovations that are developed by IBM Research as well as open source technology and are designed to reduce the time and resources that are required for a developer to add powerful AI to an application.

The Watson NLP library comes with hundreds of pretrained models in a vast assortment of global languages with dozens of modules for NLP tasks, including sentiment analysis, phrase extraction, and text classification. Using these models, you can save time and compute costs on training models and return the value of embedded AI faster.

To help you get started in AWS platform quickly using IBM Watson Libraries, Follow the following tutorials for Watson NLP and Speech library.

## Deploy Watson NLP 

### Redhat OpenShift AWS (ROSA) and EKS EC2/Fargate

- [Deploy Watson NLP models on a Kubernetes or OpenShift cluster](https://developer.ibm.com/tutorials/serve-pretrained-models-on-kubernetes-or-openshift/) 

### ECS Fargate

We demonstrate two alternative approaches to deploy Watson NLP models using ECS:

  - [Deploy with Docker Compose](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/Deploy-to-AWS-Fargate)
  - [Deploy with ECS task definition](https://github.com/ibm-build-lab/Watson-NLP/tree/main/MLOps/Watson-NLP-ECS)

## Deploy Watson Speech to Text (STT)

### Redhat OpenShift AWS (ROSA) and EKS EC2/Fargate

You can do either a customizable deployment or non-customizable. A customizable deployment allows users to specify how particular words should be written.

  - [Non-customizable deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-runtime-openshift)
  - [Customization deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-customization-openshift)

## Deploy Watson Text to Speech (TTS)

### Redhat OpenShift AWS (ROSA) and EKS EC2/Fargate

As with STT, you can deploy TTS as either a customizable or non-customizable. The customizable deployment allows the user to specify how particular words should be pronounced.

  - [Non-customizable deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-runtime-openshift)
  - [Customization deployment](https://github.com/ibm-build-lab/Watson-Speech/tree/main/tts-customization-openshift)




  

