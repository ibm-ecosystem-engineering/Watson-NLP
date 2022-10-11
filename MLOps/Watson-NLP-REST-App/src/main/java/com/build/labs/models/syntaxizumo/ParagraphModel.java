package com.build.labs.models.syntaxizumo;

public class ParagraphModel {
	private SpanModel span;

	public ParagraphModel(SpanModel span) {
		this.span = span;
	}

	public ParagraphModel() {
	}

	public SpanModel getSpan() {
		return span;
	}

	public void setSpan(SpanModel span) {
		this.span = span;
	}
}