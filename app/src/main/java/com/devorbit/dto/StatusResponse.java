package com.devorbit.dto;

public class StatusResponse {

    private String status;
    private String label;

    public StatusResponse() {
    }

    public StatusResponse(String status, String label) {
        this.status = status;
        this.label = label;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }
}

