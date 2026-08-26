package com.devorbit.dto;

import com.devorbit.model.IssueStatus;
import jakarta.validation.constraints.NotNull;

public class UpdateIssueStatusRequest {

    @NotNull(message = "Status is required (OPEN, IN_PROGRESS, RESOLVED)")
    private IssueStatus status;

    public UpdateIssueStatusRequest() {
    }

    public UpdateIssueStatusRequest(IssueStatus status) {
        this.status = status;
    }

    public IssueStatus getStatus() {
        return status;
    }

    public void setStatus(IssueStatus status) {
        this.status = status;
    }
}
