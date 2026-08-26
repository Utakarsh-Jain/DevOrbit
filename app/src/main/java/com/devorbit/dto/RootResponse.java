package com.devorbit.dto;

public class RootResponse {
    private String application;
    private String version;
    private String status;

    public RootResponse() {
    }

    public RootResponse(String application, String version, String status) {
        this.application = application;
        this.version = version;
        this.status = status;
    }

    public String getApplication() {
        return application;
    }

    public void setApplication(String application) {
        this.application = application;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
