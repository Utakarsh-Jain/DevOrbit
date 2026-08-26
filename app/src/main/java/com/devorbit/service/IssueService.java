package com.devorbit.service;

import com.devorbit.dto.CreateIssueRequest;
import com.devorbit.dto.IssueResponse;
import com.devorbit.dto.UpdateIssueStatusRequest;
import com.devorbit.exception.ResourceNotFoundException;
import com.devorbit.model.Issue;
import com.devorbit.model.IssueStatus;
import com.devorbit.repository.IssueRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class IssueService {

    private static final Logger log = LoggerFactory.getLogger(IssueService.class);
    private final IssueRepository issueRepository;

    public IssueService(IssueRepository issueRepository) {
        this.issueRepository = issueRepository;
    }

    public List<IssueResponse> getAllIssues() {
        log.info("Fetching all campus issues");
        return issueRepository.findAll()
                .stream()
                .map(IssueResponse::fromEntity)
                .collect(Collectors.toList());
    }

    public IssueResponse getIssueById(String id) {
        log.info("Fetching issue with ID: {}", id);
        Issue issue = issueRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Issue not found with ID: " + id));
        return IssueResponse.fromEntity(issue);
    }

    public IssueResponse createIssue(CreateIssueRequest request) {
        String generatedId = "ISSUE-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
        Instant now = Instant.now();

        Issue issue = new Issue(
                generatedId,
                request.getTitle().trim(),
                request.getDescription().trim(),
                IssueStatus.OPEN,
                now,
                now
        );

        Issue saved = issueRepository.save(issue);
        log.info("Created new issue: ID={}, Title={}", saved.getId(), saved.getTitle());
        return IssueResponse.fromEntity(saved);
    }

    public IssueResponse updateIssueStatus(String id, UpdateIssueStatusRequest request) {
        log.info("Updating status for issue ID: {} to {}", id, request.getStatus());
        Issue issue = issueRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Issue not found with ID: " + id));

        issue.setStatus(request.getStatus());
        issue.setUpdatedAt(Instant.now());

        Issue updated = issueRepository.save(issue);
        log.info("Successfully updated issue ID: {} status to {}", id, updated.getStatus());
        return IssueResponse.fromEntity(updated);
    }
}
