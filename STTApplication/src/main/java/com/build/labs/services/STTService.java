package com.build.labs.services;

import java.io.IOException;
import java.io.InputStream;

import org.springframework.stereotype.Service;

import com.build.labs.feignclient.FeignSTTClient;

@Service
public class STTService {
	
    private final FeignSTTClient postFeignClient;
	
	public STTService(FeignSTTClient postFeignClient) {
		super();
		this.postFeignClient = postFeignClient;
	}



	public String execute(InputStream inputStream) throws IOException { 
		
		String output = postFeignClient.stt(inputStream.readAllBytes());
	    return output;
	}
	
	/*
	public static void main(String[] args) throws FileNotFoundException {
		//new STTService().execute();
	}
	*/
}
