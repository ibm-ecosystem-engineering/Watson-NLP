package com.build.labs.services;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.build.labs.feignclient.SSTServingClient;
import com.build.labs.model.Summary;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class STTService {
	
    private final SSTServingClient postFeignClient;
    
    @Value("${client.post.baseurl}")
    private String baseUrl;
	
	public STTService(SSTServingClient postFeignClient) {
		super();
		this.postFeignClient = postFeignClient;
	}
	
	public String transcriptAudio(InputStream inputStream) throws URISyntaxException, IOException {
		String result = postFeignClient.transcript(inputStream.readAllBytes());
		return result;
	}
	
	
}
