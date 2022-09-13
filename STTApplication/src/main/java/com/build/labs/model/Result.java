
package com.build.labs.model;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Result {

	@JsonProperty("final")
    private Boolean _final;
    private List<Alternative> alternatives = null;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("final")
    public Boolean getFinal() {
        return _final;
    }

    @JsonProperty("final")
    public void setFinal(Boolean _final) {
        this._final = _final;
    }

    public List<Alternative> getAlternatives() {
        return alternatives;
    }

    public void setAlternatives(List<Alternative> alternatives) {
        this.alternatives = alternatives;
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
        sb.append(Result.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("_final");
        sb.append('=');
        sb.append(((this._final == null)?"<null>":this._final));
        sb.append(',');
        sb.append("alternatives");
        sb.append('=');
        sb.append(((this.alternatives == null)?"<null>":this.alternatives));
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
        result = ((result* 31)+((this.alternatives == null)? 0 :this.alternatives.hashCode()));
        result = ((result* 31)+((this.additionalProperties == null)? 0 :this.additionalProperties.hashCode()));
        result = ((result* 31)+((this._final == null)? 0 :this._final.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Result) == false) {
            return false;
        }
        Result rhs = ((Result) other);
        return ((((this.alternatives == rhs.alternatives)||((this.alternatives!= null)&&this.alternatives.equals(rhs.alternatives)))&&((this.additionalProperties == rhs.additionalProperties)||((this.additionalProperties!= null)&&this.additionalProperties.equals(rhs.additionalProperties))))&&((this._final == rhs._final)||((this._final!= null)&&this._final.equals(rhs._final))));
    }

}
