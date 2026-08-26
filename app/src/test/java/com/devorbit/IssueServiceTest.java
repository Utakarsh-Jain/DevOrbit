package com.devorbit;

import com.devorbit.dto.CreateIssueRequest;
import com.devorbit.dto.IssueResponse;
import com.devorbit.dto.UpdateIssueStatusRequest;
import com.devorbit.exception.ResourceNotFoundException;
import com.devorbit.model.IssueStatus;
import com.devorbit.repository.InMemoryIssueRepository;
import com.devorbit.repository.IssueRepository;
import com.devorbit.service.IssueService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

class IssueServiceTest {

    private IssueRepository issueRepository;
    private IssueService issueService;

    @BeforeEach
    void setUp() {
        issueRepository = new InMemoryIssueRepository();
        issueService = new IssueService(issueRepository);
    }

    @Test
    void shouldFetchAllIssues() {
        List<IssueResponse> issues = issueService.getAllIssues();
        assertNotNull(issues);
        assertEquals(2, issues.size());
    }

    @Test
    void shouldCreateNewIssue() {
        CreateIssueRequest request = new CreateIssueRequest("Test Title", "Detailed test description");
        IssueResponse created = issueService.createIssue(request);

        assertNotNull(created);
        assertNotNull(created.getId());
        assertEquals("Test Title", created.getTitle());
        assertEquals(IssueStatus.OPEN, created.getStatus());
    }

    @Test
    void shouldThrowExceptionWhenNotFound() {
        assertThrows(ResourceNotFoundException.class, () -> {
            issueService.getIssueById("INVALID-ID");
        });
    }

    @Test
    void shouldUpdateIssueStatus() {
        UpdateIssueStatusRequest request = new UpdateIssueStatusRequest(IssueStatus.IN_PROGRESS);
        IssueResponse updated = issueService.updateIssueStatus("ISSUE-101", request);

        assertNotNull(updated);
        assertEquals(IssueStatus.IN_PROGRESS, updated.getStatus());
    }
}
