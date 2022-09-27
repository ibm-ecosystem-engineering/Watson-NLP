package com.build.labs.models.syntaxizumo;

public class SpanModel {
	private int begin;
	private int end;
	private String text;

	public SpanModel(int begin, int end, String text) {
		this.begin = begin;
		this.end = end;
		this.text = text;
	}

	public SpanModel() {
	}

	public int getBegin() {
		return begin;
	}

	public void setBegin(int begin) {
		this.begin = begin;
	}

	public int getEnd() {
		return end;
	}

	public void setEnd(int end) {
		this.end = end;
	}

	public String getText() {
		return text;
	}

	public void setText(String text) {
		this.text = text;
	}

}