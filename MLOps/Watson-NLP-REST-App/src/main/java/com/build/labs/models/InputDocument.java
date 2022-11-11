package com.build.labs.models;

public class InputDocument {
	private RawDocument rawDocument;

	public InputDocument() {
		super();
	}

	public InputDocument(RawDocument rawDocument) {
		super();
		this.rawDocument = rawDocument;
	}

	public RawDocument getRawDocument() {
		return rawDocument;
	}

	public void setRawDocument(RawDocument rawDocument) {
		this.rawDocument = rawDocument;
	}

}
