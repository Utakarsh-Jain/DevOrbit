package com.devorbit.dto;

public class RootResponse {
    private String application;
    private String version;
    private String status;
    private String environment;
    private UiConfigurationResponse ui;

    public RootResponse() {
    }

    public RootResponse(String application, String version, String status, String environment) {
        this(application, version, status, environment, null);
    }

    public RootResponse(String application, String version, String status, String environment,
                        UiConfigurationResponse ui) {
        this.application = application;
        this.version = version;
        this.status = status;
        this.environment = environment;
        this.ui = ui;
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

    public UiConfigurationResponse getUi() {
        return ui;
    }

    public void setUi(UiConfigurationResponse ui) {
        this.ui = ui;
    }
}
