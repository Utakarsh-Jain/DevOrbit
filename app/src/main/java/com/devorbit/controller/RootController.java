package com.devorbit.controller;

import com.devorbit.dto.RootResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/")
public class RootController {

    @Value("${app.name:DevOrbit Campus Issue Management}")
    private String appName;

    @Value("${app.version:1.0.0}")
    private String appVersion;

    @GetMapping
    public ResponseEntity<RootResponse> getRootInfo() {
        RootResponse response = new RootResponse(appName, appVersion, "running");
        return ResponseEntity.ok(response);
    }
}
