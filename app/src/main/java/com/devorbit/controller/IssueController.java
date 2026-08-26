package com.devorbit.controller;

import com.devorbit.dto.CreateIssueRequest;
import com.devorbit.dto.IssueResponse;
import com.devorbit.dto.UpdateIssueStatusRequest;
import com.devorbit.service.IssueService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/issues")
public class IssueController {

    private final IssueService issueService;

    public IssueController(IssueService issueService) {
        this.issueService = issueService;
    }

    @GetMapping
    public ResponseEntity<List<IssueResponse>> getAllIssues() {
        return ResponseEntity.ok(issueService.getAllIssues());
    }

    @GetMapping("/{id}")
    public ResponseEntity<IssueResponse> getIssueById(@PathVariable String id) {
        return ResponseEntity.ok(issueService.getIssueById(id));
    }

    @PostMapping
    public ResponseEntity<IssueResponse> createIssue(@Valid @RequestBody CreateIssueRequest request) {
        IssueResponse created = issueService.createIssue(request);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<IssueResponse> updateIssueStatus(
            @PathVariable String id,
            @Valid @RequestBody UpdateIssueStatusRequest request) {
        IssueResponse updated = issueService.updateIssueStatus(id, request);
        return ResponseEntity.ok(updated);
    }
}
