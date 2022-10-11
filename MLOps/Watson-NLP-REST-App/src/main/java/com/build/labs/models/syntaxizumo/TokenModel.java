package com.build.labs.models.syntaxizumo;

import java.util.List;

public class TokenModel {
	private SpanModel span;
	private String lemma;
	private String partOfSpeech;
	private String dependency;
	private List<String> features;

	public TokenModel(SpanModel span, String lemma, String partOfSpeech, String dependency, List<String> features) {
		super();
		this.span = span;
		this.lemma = lemma;
		this.partOfSpeech = partOfSpeech;
		this.dependency = dependency;
		this.features = features;
	}

	public TokenModel() {
	}

	public SpanModel getSpan() {
		return span;
	}

	public void setSpan(SpanModel span) {
		this.span = span;
	}

	public String getLemma() {
		return lemma;
	}

	public void setLemma(String lemma) {
		this.lemma = lemma;
	}

	public String getPartOfSpeech() {
		return partOfSpeech;
	}

	public void setPartOfSpeech(String partOfSpeech) {
		this.partOfSpeech = partOfSpeech;
	}

	public String getDependency() {
		return dependency;
	}

	public void setDependency(String dependency) {
		this.dependency = dependency;
	}

	public List<String> getFeatures() {
		return features;
	}

	public void setFeatures(List<String> features) {
		this.features = features;
	}

}