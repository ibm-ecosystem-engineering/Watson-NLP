package com.build.labs.services;

import org.springframework.stereotype.Service;
import com.build.labs.dto.CommonRequestDto;
import com.build.labs.feign.FeignModelInferenceClient;

@Service
public class CommonModelService {

	private final FeignModelInferenceClient postFeignClient;

	public CommonModelService(FeignModelInferenceClient postFeignClient) {
		super();
		this.postFeignClient = postFeignClient;
	}

	public String predict(CommonRequestDto commonRequest) {
		BaseService modelService = ModelFactory.getModel(commonRequest);
		return modelService.serve(commonRequest, postFeignClient);
	}

}
