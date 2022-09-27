package com.build.labs.services;

import com.build.labs.dto.CommonRequestDto;
import com.build.labs.feign.FeignModelInferenceClient;

public interface BaseService {
	String MODEL_ID_KEY = "grpc-metadata-mm-model-id";
	<T> T serve(CommonRequestDto commonRequest, FeignModelInferenceClient postFeignClient);
}
