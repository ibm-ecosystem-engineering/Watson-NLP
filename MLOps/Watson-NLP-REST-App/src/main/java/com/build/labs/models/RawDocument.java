package com.build.labs.models;

public class RawDocument {
	private String text;

	public RawDocument(String text) {
		super();
		this.text = text;
	}

	public RawDocument() {
		super();
	}

	public String getText() {
		return text;
	}

	public void setText(String value) {
		this.text = value;
	}
}
