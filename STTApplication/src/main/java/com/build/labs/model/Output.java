package com.build.labs.model;

public class Output {
	private String transcript;
	private Double confidence;

	public Output() {

	}

	public Output(String transcript, Double confidence) {
		this.transcript = transcript;
		this.confidence = confidence;
	}

	public String getTranscript() {
		return transcript;
	}

	public void setTranscript(String transcript) {
		this.transcript = transcript;
	}

	public Double getConfidence() {
		return confidence;
	}

	public void setConfidence(Double confidence) {
		this.confidence = confidence;
	}

}
