package com.build.labs.models.syntaxizumo;

public class SentenceModel {
	private SpanModel span;

	public SentenceModel(SpanModel span) {
		this.span = span;
	}

	public SentenceModel() {
	}

	public SpanModel getSpan() {
		return span;
	}

	public void setSpan(SpanModel span) {
		this.span = span;
	}
}