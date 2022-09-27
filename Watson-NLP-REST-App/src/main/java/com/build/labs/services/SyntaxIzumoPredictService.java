package com.build.labs.services;

import org.springframework.http.HttpHeaders;

import com.build.labs.dto.CommonRequestDto;
import com.build.labs.feign.FeignModelInferenceClient;
import com.build.labs.models.InputDocument;
import com.build.labs.models.RawDocument;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class SyntaxIzumoPredictService implements BaseService {
	
	public SyntaxIzumoPredictService() {
	}

	@SuppressWarnings("unchecked")
	@Override
	public String serve(CommonRequestDto commonRequest, FeignModelInferenceClient postFeignClient) {
		HttpHeaders headers = new HttpHeaders();
		headers.add(MODEL_ID_KEY, commonRequest.getModel_id());
		RawDocument document = new RawDocument();
		InputDocument inputDoc = new InputDocument(document);
		document.setText(commonRequest.getInput_text());
		String result = postFeignClient.syntaxIzumoRequest(headers, inputDoc);
		ObjectMapper mapper = new ObjectMapper();
		try {
			mapper.writerWithDefaultPrettyPrinter().writeValueAsString(result);
		} catch (JsonProcessingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return result;
	}

}
