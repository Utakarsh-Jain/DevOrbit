package com.devorbit.repository;

import com.devorbit.model.Issue;

import java.util.List;
import java.util.Optional;

public interface IssueRepository {
    Issue save(Issue issue);
    Optional<Issue> findById(String id);
    List<Issue> findAll();
    boolean deleteById(String id);
    void clear();
}
