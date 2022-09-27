package com.build.labs.models.syntaxizumo;

import java.util.List;

public class SyntaxPredictionModel {
	private String text;
	private List<TokenModel> tokens;
	private List<SentenceModel> sentences;
	private List<ParagraphModel> paragraphs;

	public SyntaxPredictionModel() {

	}

	public String getText() {
		return text;
	}

	public void setText(String text) {
		this.text = text;
	}

	public List<TokenModel> getTokens() {
		return tokens;
	}

	public void setTokens(List<TokenModel> tokens) {
		this.tokens = tokens;
	}

	public List<SentenceModel> getSentences() {
		return sentences;
	}

	public void setSentences(List<SentenceModel> sentences) {
		this.sentences = sentences;
	}

	public List<ParagraphModel> getParagraphs() {
		return paragraphs;
	}

	public void setParagraphs(List<ParagraphModel> paragraphs) {
		this.paragraphs = paragraphs;
	}

}