# DevOrbit System Architecture

## Overview
DevOrbit is an academic cloud-native DevOps project designed to demonstrate the complete, automated software delivery lifecycle.

```text
+------------------------------------------------------------------------------------+
|                                 APPLICATION LIFECYCLE                              |
|                                                                                    |
|   Developer ──> GitHub ──> Jenkins ──> Maven Build & Test ──> Docker Image        |
|                                                                     │              |
|                                                                     v              |
|                                                              Docker Registry       |
|                                                                     │              |
|                                                                     v              |
|                                                           Kubernetes (k3s)         |
|                                                                     │              |
|                                                                     v              |
|                                                              AWS CloudWatch        |
+------------------------------------------------------------------------------------+

+------------------------------------------------------------------------------------+
|                              INFRASTRUCTURE LIFECYCLE                              |
|                                                                                    |
|   Terraform ──> AWS Infrastructure (VPC, Subnet, EC2, SG, Alarms)                  |
|        │                                                                           |
|        v                                                                           |
|     Ansible ──> Configured Linux Host (Docker CE + Java 21 + k3s Cluster)          |
+------------------------------------------------------------------------------------+
```

## Architectural Components

1. **Spring Boot Microservice (`app/`)**:
   - Lightweight Java REST API for campus issue management.
   - Built with Maven, tested with JUnit 5, containerized into Alpine JRE.
2. **Infrastructure as Code (`terraform/`)**:
   - Fully declarative AWS provisioning covering VPC, subnets, route tables, security groups, and EC2 instances.
3. **Configuration Automation (`ansible/`)**:
   - Automated post-provisioning configuration of host packages, Docker daemon, and k3s single-node cluster.
4. **Container Orchestration (`k8s/`)**:
   - Isolated `devorbit` namespace, ConfigMap configuration, rolling update deployment with 2 replicas, readiness & liveness probes, and NodePort routing.
5. **Continuous Integration & Delivery (`jenkins/`)**:
   - 8-stage automated Jenkins pipeline triggered upon GitHub push/merge.
6. **Observability (`AWS CloudWatch`)**:
   - EC2 CPU utilization alarms, container status monitoring, and system metrics.
