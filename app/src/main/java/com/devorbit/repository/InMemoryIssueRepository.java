package com.devorbit.repository;

import com.devorbit.model.Issue;
import com.devorbit.model.IssueStatus;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryIssueRepository implements IssueRepository {

    private final Map<String, Issue> storage = new ConcurrentHashMap<>();

    public InMemoryIssueRepository() {
        initSampleData();
    }

    private void initSampleData() {
        Issue issue1 = new Issue(
                "ISSUE-101",
                "Lab 3 Projector HDMI Fault",
                "Projector display flickering intermittently during cloud computing lab.",
                IssueStatus.OPEN,
                Instant.now().minusSeconds(86400),
                Instant.now().minusSeconds(86400)
        );
        Issue issue2 = new Issue(
                "ISSUE-102",
                "Library 2nd Floor Wi-Fi Signal Degradation",
                "Students experiencing packet drops and low bandwidth in study area.",
                IssueStatus.IN_PROGRESS,
                Instant.now().minusSeconds(43200),
                Instant.now().minusSeconds(10000)
        );
        storage.put(issue1.getId(), issue1);
        storage.put(issue2.getId(), issue2);
    }

    @Override
    public Issue save(Issue issue) {
        storage.put(issue.getId(), issue);
        return issue;
    }

    @Override
    public Optional<Issue> findById(String id) {
        return Optional.ofNullable(storage.get(id));
    }

    @Override
    public List<Issue> findAll() {
        List<Issue> issues = new ArrayList<>(storage.values());
        issues.sort(Comparator.comparing(Issue::getCreatedAt).reversed());
        return issues;
    }

    @Override
    public boolean deleteById(String id) {
        return storage.remove(id) != null;
    }

    @Override
    public void clear() {
        storage.clear();
    }
}
