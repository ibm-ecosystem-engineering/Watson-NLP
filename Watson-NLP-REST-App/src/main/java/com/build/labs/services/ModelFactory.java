package com.build.labs.services;

import com.build.labs.dto.CommonRequestDto;

public class ModelFactory {

	public static BaseService getModel(CommonRequestDto commonRequest) {
		BaseService service = null;
		switch (commonRequest.getCommon_service()) {
		case "SyntaxIzumoPredict":
			service = new SyntaxIzumoPredictService();
			break;
		default:
			throw new IllegalArgumentException("Invalid service name provided");
		}
		return service;
	}

}
