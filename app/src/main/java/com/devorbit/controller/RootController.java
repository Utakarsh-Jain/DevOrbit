package com.devorbit.controller;

import com.devorbit.dto.RootResponse;
import com.devorbit.dto.UiConfigurationResponse;
import com.devorbit.model.IssueStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;

@RestController
@RequestMapping("/")
public class RootController {

    @Value("${app.name:DevOrbit Campus Issue Management}")
    private String appName;

    @Value("${app.version:1.0.0}")
    private String appVersion;

    @Value("${app.environment:local}")
    private String appEnvironment;

    @Value("${app.ui.subtitle:Campus Issue Management}")
    private String uiSubtitle;

    @Value("${app.ui.issue-title.min-length:3}")
    private int issueTitleMinLength;

    @Value("${app.ui.issue-title.max-length:100}")
    private int issueTitleMaxLength;

    @Value("${app.ui.issue-description.min-length:5}")
    private int issueDescriptionMinLength;

    @Value("${app.ui.issue-description.max-length:1000}")
    private int issueDescriptionMaxLength;

    @GetMapping
    public ResponseEntity<RootResponse> getRootInfo() {
        UiConfigurationResponse ui = new UiConfigurationResponse(
                appName,
                uiSubtitle,
                Arrays.stream(IssueStatus.values())
                        .map(status -> new UiConfigurationResponse.StatusOption(status.name(), status.getLabel()))
                        .toList(),
                new UiConfigurationResponse.EndpointConfiguration("/health", "/api/issues"),
                new UiConfigurationResponse.FormConfiguration(
                        issueTitleMinLength, issueTitleMaxLength,
                        issueDescriptionMinLength, issueDescriptionMaxLength
                )
        );
        RootResponse response = new RootResponse(appName, appVersion, "running", appEnvironment, ui);
        return ResponseEntity.ok(response);
    }
}
