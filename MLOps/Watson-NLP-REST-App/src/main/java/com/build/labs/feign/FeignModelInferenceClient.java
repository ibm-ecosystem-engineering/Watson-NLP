package com.build.labs.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

import com.build.labs.models.InputDocument;

@FeignClient(name = "nlpFeignClient", url = "${client.post.baseurl}")
public interface FeignModelInferenceClient {

	public final String NLP_REST_MAPPING = "/v1/watson_runtime/NlpService/SyntaxPredict";

	@PostMapping(path = NLP_REST_MAPPING, consumes = MediaType.APPLICATION_JSON_VALUE)
	String syntaxIzumoRequest(@RequestHeader HttpHeaders headers, @RequestBody InputDocument rawDocument);
}
