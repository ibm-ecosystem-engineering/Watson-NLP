package com.build.labs.feignclient;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import feign.Headers;

@FeignClient(name = "sttFeignClient", url = "${client.post.baseurl}")
public interface FeignSTTClient {
	
	public final String STT_REST_MAPPING = "/speech-to-text/api/v1/recognize?model=en-US_Multimedia";
	
	@PostMapping(STT_REST_MAPPING)
    @Headers({
            "Content-Type: audio/wav"
    })
    String stt(byte[] blob);
}