package com.devorbit.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CreateIssueRequest {

    @NotBlank(message = "Title is required and must not be blank")
    @Size(min = 3, max = 100, message = "Title must be between 3 and 100 characters")
    private String title;

    @NotBlank(message = "Description is required and must not be blank")
    @Size(min = 5, max = 1000, message = "Description must be between 5 and 1000 characters")
    private String description;

    public CreateIssueRequest() {
    }

    public CreateIssueRequest(String title, String description) {
        this.title = title;
        this.description = description;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
