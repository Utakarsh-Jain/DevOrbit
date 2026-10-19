package com.devorbit;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.devorbit.dto.CreateIssueRequest;
import com.devorbit.dto.UpdateIssueStatusRequest;
import com.devorbit.model.IssueStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class IssueControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void shouldGetAllIssues() throws Exception {
        mockMvc.perform(get("/api/issues"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    void shouldGetIssueById() throws Exception {
        mockMvc.perform(get("/api/issues/ISSUE-101"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("ISSUE-101"))
                .andExpect(jsonPath("$.title").value("Lab 3 Projector HDMI Fault"))
                .andExpect(jsonPath("$.status").exists());
    }

    @Test
    void shouldReturn404WhenIssueNotFound() throws Exception {
        mockMvc.perform(get("/api/issues/NON-EXISTING-999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("NOT_FOUND"));
    }

    @Test
    void shouldCreateNewIssueSuccessfully() throws Exception {
        CreateIssueRequest request = new CreateIssueRequest(
                "CS Lab 1 Workstation 5 Power Supply",
                "Workstation is not powering on after power surge in computer lab."
        );

        mockMvc.perform(post("/api/issues")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.title").value("CS Lab 1 Workstation 5 Power Supply"))
                .andExpect(jsonPath("$.status").value("OPEN"))
                .andExpect(jsonPath("$.createdAt").exists())
                .andExpect(jsonPath("$.updatedAt").exists());
    }

    @Test
    void shouldReturn400WhenCreateIssueValidationFails() throws Exception {
        CreateIssueRequest invalidRequest = new CreateIssueRequest("", "");

        mockMvc.perform(post("/api/issues")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.details").isArray());
    }

    @Test
    void shouldReturn400WhenJsonIsMalformed() throws Exception {
        mockMvc.perform(post("/api/issues")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{ this is not valid json }"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("MALFORMED_JSON"));
    }

    @Test
    void shouldReturn400WhenStatusIsInvalid() throws Exception {
        mockMvc.perform(patch("/api/issues/ISSUE-101")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"NOT_A_REAL_STATUS\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("MALFORMED_JSON"));
    }

    @Test
    void shouldUpdateIssueStatusSuccessfully() throws Exception {
        CreateIssueRequest createRequest = new CreateIssueRequest(
                "Wi-Fi Access Point Reset",
                "Access point on the first floor needs a status update test."
        );
        String createdBody = mockMvc.perform(post("/api/issues")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        String createdId = objectMapper.readTree(createdBody).get("id").asText();

        UpdateIssueStatusRequest request = new UpdateIssueStatusRequest(IssueStatus.RESOLVED);

        mockMvc.perform(patch("/api/issues/" + createdId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(createdId))
                .andExpect(jsonPath("$.status").value("RESOLVED"));
    }

    @Test
    void shouldReturn404WhenPatchingNonExistingIssue() throws Exception {
        UpdateIssueStatusRequest request = new UpdateIssueStatusRequest(IssueStatus.RESOLVED);

        mockMvc.perform(patch("/api/issues/DOES-NOT-EXIST")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }
}
