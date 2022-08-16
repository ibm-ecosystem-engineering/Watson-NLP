FROM <BASE_RUNTIME_WATSON_NLP> as base
ENV ARTIFACTORY_USERNAME <IBM ID>
ENV ARTIFACTORY_API_KEY <ENTITLEMENT_API_KEY>
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 list
EXPOSE 8050
RUN groupadd appuser && adduser -g appuser appuser && usermod -aG appuser appuser
RUN chown -R appuser:appuser /app
USER appuser
COPY . /app
ENTRYPOINT ["python3","Sentiment_dash_app.py"]
