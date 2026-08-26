# Continuous Integration & Continuous Delivery (CI/CD)

## Definitions
- **Continuous Integration (CI)**: The engineering practice where developers integrate code frequently into a shared repository, verified by automated compilation and tests.
- **Continuous Delivery (CD)**: Automating the packaging and release readiness so validated artifacts can be deployed to target environments on demand.
- **Continuous Deployment**: Extending CD so that every passing build is automatically deployed directly to the production cluster without manual intervention.

## Pipeline Traceability
Every container image built by DevOrbit is uniquely identified with:
`devorbit-app:${BUILD_NUMBER}-${GIT_COMMIT_SHA}`
This eliminates ambiguity regarding which source revision is running in the cluster.
