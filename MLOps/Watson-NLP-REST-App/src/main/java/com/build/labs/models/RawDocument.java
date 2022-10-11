package com.build.labs.models;

public class RawDocument {
	private String text;
	
	public RawDocument(String text) {
		super();
		this.text = text;
	}

	public RawDocument() {
		super();
		// TODO Auto-generated constructor stub
	}

	public String getText() {
		return text;
	}

	public void setText(String value) {
		this.text = value;
	}
}
