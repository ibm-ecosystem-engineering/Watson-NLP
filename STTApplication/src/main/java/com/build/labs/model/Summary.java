
package com.build.labs.model;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Summary {

	@JsonProperty("result_index")
    private Integer resultIndex;
    private List<Result> results = null;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("result_index")
    public Integer getResultIndex() {
        return resultIndex;
    }

    @JsonProperty("result_index")
    public void setResultIndex(Integer resultIndex) {
        this.resultIndex = resultIndex;
    }

    public List<Result> getResults() {
        return results;
    }

    public void setResults(List<Result> results) {
        this.results = results;
    }

    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(Summary.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("resultIndex");
        sb.append('=');
        sb.append(((this.resultIndex == null)?"<null>":this.resultIndex));
        sb.append(',');
        sb.append("results");
        sb.append('=');
        sb.append(((this.results == null)?"<null>":this.results));
        sb.append(',');
        sb.append("additionalProperties");
        sb.append('=');
        sb.append(((this.additionalProperties == null)?"<null>":this.additionalProperties));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.additionalProperties == null)? 0 :this.additionalProperties.hashCode()));
        result = ((result* 31)+((this.results == null)? 0 :this.results.hashCode()));
        result = ((result* 31)+((this.resultIndex == null)? 0 :this.resultIndex.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Summary) == false) {
            return false;
        }
        Summary rhs = ((Summary) other);
        return ((((this.additionalProperties == rhs.additionalProperties)||((this.additionalProperties!= null)&&this.additionalProperties.equals(rhs.additionalProperties)))&&((this.results == rhs.results)||((this.results!= null)&&this.results.equals(rhs.results))))&&((this.resultIndex == rhs.resultIndex)||((this.resultIndex!= null)&&this.resultIndex.equals(rhs.resultIndex))));
    }

}
