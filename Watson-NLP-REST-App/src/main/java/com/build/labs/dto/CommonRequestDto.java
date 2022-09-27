package com.build.labs.dto;

public class CommonRequestDto {
	private String model_id;
	private String common_service;
	private String input_text;

	public CommonRequestDto() {

	}

	public CommonRequestDto(String model_id, String common_service, String input_text) {
		this.model_id = model_id;
		this.common_service = common_service;
		this.input_text = input_text;
	}

	public String getModel_id() {
		return model_id;
	}

	public void setModel_id(String model_id) {
		this.model_id = model_id;
	}

	public String getCommon_service() {
		return common_service;
	}

	public void setCommon_service(String common_service) {
		this.common_service = common_service;
	}

	public String getInput_text() {
		return input_text;
	}

	public void setInput_text(String input_text) {
		this.input_text = input_text;
	}

	@Override
	public String toString() {
		return "SyntaxIzumoRequest [model_id=" + model_id + ", common_service=" + common_service + ", input_text="
				+ input_text + "]";
	}
}
