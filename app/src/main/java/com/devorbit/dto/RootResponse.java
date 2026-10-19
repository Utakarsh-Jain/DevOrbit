package com.devorbit.dto;

public class RootResponse {
    private String application;
    private String version;
    private String status;
    private String environment;

    public RootResponse() {
    }

    public RootResponse(String application, String version, String status, String environment) {
        this.application = application;
        this.version = version;
        this.status = status;
        this.environment = environment;
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

    public String getEnvironment() {
        return environment;
    }

    public void setEnvironment(String environment) {
        this.environment = environment;
    }
}
