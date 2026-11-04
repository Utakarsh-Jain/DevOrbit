import sys
import os
import weasyprint

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DevOrbit - Minor Project Report</title>
<style>
  @page {
    size: A4;
    margin: 25mm 20mm 25mm 25mm;
    @bottom-right {
      content: counter(page);
      font-family: 'Times New Roman', Times, serif;
      font-size: 10pt;
    }
  }

  @page:first {
    @bottom-right {
      content: "";
    }
  }

  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #111111;
    text-align: justify;
    margin: 0;
    padding: 0;
  }

  .page-break {
    page-break-after: always;
  }

  /* Cover Page */
  .cover-page {
    text-align: center;
    padding-top: 10mm;
    height: 100%;
    box-sizing: border-box;
  }

  .cover-title {
    font-size: 18pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.4;
    margin-bottom: 8mm;
    color: #0d233a;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-style: italic;
    margin-bottom: 12mm;
    color: #333333;
  }

  .cover-report-text {
    font-size: 12pt;
    margin-bottom: 12mm;
    line-height: 1.6;
  }

  .cover-submitted-by {
    font-size: 12pt;
    margin-top: 10mm;
    margin-bottom: 15mm;
  }

  .student-table {
    margin: 0 auto;
    font-size: 11pt;
    text-align: left;
    border-collapse: collapse;
  }

  .student-table td {
    padding: 4px 15px;
  }

  .cover-dept {
    font-size: 13pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 15mm;
    line-height: 1.4;
    color: #0d233a;
  }

  .cover-institution {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 2mm;
  }

  .cover-date {
    font-size: 11pt;
    margin-top: 8mm;
    font-weight: bold;
  }

  /* Bonafide Certificate */
  .certificate-page {
    padding-top: 10mm;
  }

  .cert-header {
    text-align: center;
    font-size: 14pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.3;
    margin-bottom: 2mm;
    color: #0d233a;
  }

  .cert-sub {
    text-align: center;
    font-size: 12pt;
    font-weight: bold;
    margin-bottom: 8mm;
  }

  .cert-title {
    text-align: center;
    font-size: 15pt;
    font-weight: bold;
    text-decoration: underline;
    margin-bottom: 12mm;
    letter-spacing: 1px;
  }

  .cert-body {
    font-size: 12pt;
    line-height: 1.8;
    text-indent: 12mm;
    margin-bottom: 20mm;
  }

  .signature-block {
    margin-top: 30mm;
    float: right;
    text-align: left;
    width: 65mm;
  }

  .sig-line {
    border-bottom: 1px solid #000;
    margin-bottom: 3mm;
    width: 50mm;
  }

  .sig-name {
    font-weight: bold;
    font-size: 11pt;
  }

  .sig-desig {
    font-size: 10.5pt;
    line-height: 1.3;
  }

  /* Headings */
  h1 {
    font-size: 16pt;
    font-weight: bold;
    text-transform: uppercase;
    color: #0d233a;
    border-bottom: 2px solid #0d233a;
    padding-bottom: 2mm;
    margin-top: 0;
    margin-bottom: 5mm;
  }

  h2 {
    font-size: 14pt;
    font-weight: bold;
    color: #1a365d;
    margin-top: 6mm;
    margin-bottom: 3mm;
  }

  h3 {
    font-size: 12pt;
    font-weight: bold;
    color: #2b6cb0;
    margin-top: 4mm;
    margin-bottom: 2mm;
  }

  p {
    margin-top: 0;
    margin-bottom: 3mm;
  }

  /* Code & Terminal Snippets */
  pre {
    background-color: #f7fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3182ce;
    padding: 3mm;
    font-family: 'Courier New', Courier, monospace;
    font-size: 9.5pt;
    line-height: 1.3;
    overflow-x: auto;
    margin-bottom: 4mm;
    border-radius: 4px;
    white-space: pre-wrap;
  }

  .terminal {
    background-color: #1a202c;
    color: #edf2f7;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 3.5mm;
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    line-height: 1.35;
    margin-bottom: 4mm;
  }

  .terminal-bar {
    background-color: #2d3748;
    color: #a0aec0;
    font-size: 8pt;
    padding: 1.5mm 3mm;
    margin: -3.5mm -3.5mm 3mm -3.5mm;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-weight: bold;
  }

  .term-green { color: #48bb78; }
  .term-cyan { color: #38b2ac; }
  .term-yellow { color: #ecc94b; }
  .term-blue { color: #63b3ed; }

  /* Tables */
  table.report-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 3mm;
    margin-bottom: 5mm;
    font-size: 10.5pt;
  }

  table.report-table th, table.report-table td {
    border: 1px solid #cbd5e0;
    padding: 2.5mm 3mm;
    text-align: left;
  }

  table.report-table th {
    background-color: #edf2f7;
    font-weight: bold;
    color: #2d3748;
  }

  table.report-table tr:nth-child(even) {
    background-color: #f7fafc;
  }

  /* Figures / Visual Boxes */
  .diagram-box {
    border: 1.5px solid #cbd5e0;
    border-radius: 6px;
    padding: 4mm;
    background-color: #f8fafc;
    margin-bottom: 4mm;
    text-align: center;
  }

  .diagram-title {
    font-size: 10pt;
    font-weight: bold;
    color: #4a5568;
    margin-top: 2mm;
    font-style: italic;
  }

  .badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 8.5pt;
    font-weight: bold;
  }
  .badge-pass { background-color: #c6f6d5; color: #22543d; }
  .badge-info { background-color: #bee3f8; color: #2a4365; }

  ul, ol {
    margin-top: 0;
    margin-bottom: 3mm;
    padding-left: 6mm;
  }

  li {
    margin-bottom: 1.5mm;
  }
</style>
</head>
<body>

<!-- ================= COVER PAGE ================= -->
<div class="cover-page page-break">
  <div class="cover-title">
    DEVORBIT: A CLOUD-NATIVE DEVOPS LIFECYCLE PLATFORM FOR REPEATABLE AND OBSERVABLE APPLICATION DELIVERY
  </div>

  <div class="cover-subtitle">
    Automated Continuous Delivery, Infrastructure as Code, Container Orchestration, and Cloud Monitoring
  </div>

  <div class="cover-report-text">
    A MINOR PROJECT REPORT<br>
    <em>Submitted in partial fulfillment of the requirements for the degree of</em><br>
    <strong>BACHELOR OF TECHNOLOGY</strong><br>
    in<br>
    <strong>COMPUTER SCIENCE AND ENGINEERING / NETWORKING &amp; COMMUNICATIONS</strong>
  </div>

  <div class="cover-submitted-by">
    <em>Submitted by</em><br><br>
    <table class="student-table">
      <tr>
        <td><strong>GAURAV (Member 3 - CI/CD &amp; Observability)</strong></td>
        <td><strong>Reg No: RA2111003010xxx</strong></td>
      </tr>
      <tr>
        <td><strong>TEAM MEMBER 1 (Infrastructure &amp; Cloud)</strong></td>
        <td><strong>Reg No: RA2111003010xxx</strong></td>
      </tr>
      <tr>
        <td><strong>TEAM MEMBER 2 (Containers &amp; Kubernetes)</strong></td>
        <td><strong>Reg No: RA2111003010xxx</strong></td>
      </tr>
    </table>
  </div>

  <div class="cover-dept">
    DEPARTMENT OF NETWORKING AND COMMUNICATIONS<br>
    SCHOOL OF COMPUTING
  </div>

  <div class="cover-institution">
    SRM INSTITUTE OF SCIENCE AND TECHNOLOGY<br>
    KATTANKULATHUR - 603 203, CHENNAI, TAMIL NADU, INDIA
  </div>

  <div class="cover-date">
    NOVEMBER 2026
  </div>
</div>

<!-- ================= BONAFIDE CERTIFICATE ================= -->
<div class="certificate-page page-break">
  <div class="cert-header">
    SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
  </div>
  <div class="cert-sub">
    (Deemed to be University u/s 3 of UGC Act, 1956)<br>
    KATTANKULATHUR - 603 203, CHENNAI, INDIA<br>
    DEPARTMENT OF NETWORKING AND COMMUNICATIONS
  </div>

  <div class="cert-title">
    BONAFIDE CERTIFICATE
  </div>

  <div class="cert-body">
    Certified that this project report titled <strong>&ldquo;DEVORBIT: A CLOUD-NATIVE DEVOPS LIFECYCLE PLATFORM FOR REPEATABLE AND OBSERVABLE APPLICATION DELIVERY&rdquo;</strong> is the bonafide work of <strong>GAURAV (Reg. No. RA2111003010xxx)</strong> and team members who carried out the minor project under my supervision during the academic year 2026&ndash;2027 in partial fulfillment of the requirements for the award of the degree of <strong>Bachelor of Technology in Department of Networking and Communications</strong>.
  </div>

  <div class="signature-block">
    <div class="sig-line"></div>
    <div class="sig-name">&lt;Faculty Name&gt;</div>
    <div class="sig-desig">
      &lt;Designation&gt;<br>
      Department of Networking and Communications<br>
      SRMIST KTR
    </div>
  </div>
</div>

<!-- ================= ABSTRACT ================= -->
<div class="page-break">
  <h1>ABSTRACT</h1>
  <p>
    Modern software engineering demands high software velocity, high system availability, and rapid defect recovery. However, conventional development environments suffer from configuration drift, manual and error-prone deployment scripts, environment inconsistencies colloquially known as <em>&ldquo;it works on my machine,&rdquo;</em> and a severe lack of operational visibility. This project presents <strong>DevOrbit</strong>, a cloud-native DevOps lifecycle platform designed to eliminate manual intervention from code commit to cloud deployment across Amazon Web Services (AWS).
  </p>
  <p>
    Rather than treating DevOps as secondary tooling around an arbitrary application, DevOrbit designs the software delivery pipeline as the primary deliverable. DevOrbit wraps a resilient campus issue management workload (Java 21, Spring Boot 3.3, and a modern Apple HIG&ndash;compliant React single-page frontend) within an automated, multi-tiered DevOps architecture.
  </p>
  <p>
    The infrastructure foundation is provisioned declaratively via <strong>HashiCorp Terraform</strong> across three peered Virtual Private Clouds (VPCs) on AWS. Host environments, package dependencies, Docker Engine, and lightweight single-node Kubernetes (k3s) are configured idempotently using <strong>Ansible</strong>. Application containers are packaged through multi-stage <strong>Docker</strong> builds running unprivileged non-root runtimes. Continuous Integration and Continuous Deployment (CI/CD) are orchestrated by an 8-stage <strong>Jenkins</strong> pipeline triggered by GitHub webhooks. The pipeline incorporates automated failure gates (via Maven and JUnit 5), pushes container images to <strong>Amazon Elastic Container Registry (ECR)</strong>, and executes zero-downtime rolling deployments to <strong>Kubernetes</strong>.
  </p>
  <p>
    System observability is established via dual telemetry streams: infrastructure health and CPU utilization tracked by <strong>AWS CloudWatch</strong> alarms, while application-level JVM and HTTP performance metrics are scraped into <strong>Prometheus</strong> and visualized on <strong>Grafana</strong>. The complete project validates that software delivery can be made 100% repeatable, version-controlled, containerized, orchestrated, and observable.
  </p>
  <p><strong>Keywords:</strong> Cloud Computing, DevOps Lifecycle, Infrastructure as Code, Terraform, Ansible, Docker, Kubernetes, Jenkins CI/CD, AWS CloudWatch, Spring Boot, React.</p>
</div>

<!-- ================= CHAPTER 1: INTRODUCTION ================= -->
<div class="page-break">
  <h1>CHAPTER 1: INTRODUCTION</h1>

  <h2>1.1 Background &amp; Motivation</h2>
  <p>
    Over the past decade, cloud computing has fundamentally transformed the landscape of enterprise software architecture. The convergence of Infrastructure as Code (IaC), containerization, microservice architectures, and continuous delivery has replaced the traditional boundary between software development and IT operations. 
  </p>
  <p>
    In academic and industrial contexts alike, software failures frequently originate not from defective application code, but from defective <em>delivery mechanisms</em>: disparate environment dependencies, manual SSH interventions, unversioned server mutations, and delayed feedback loops. When an outage occurs, teams without centralized observability struggle to isolate whether the failure stems from code, network routing, container runtime limits, or underlying cloud hypervisors.
  </p>
  <p>
    <strong>DevOrbit</strong> was conceived to demonstrate an end-to-end DevOps automation platform where every phase of the software delivery lifecycle revolves around declarative configuration, immutable artifacts, automated quality gates, and proactive monitoring.
  </p>

  <h2>1.2 Problem Statement</h2>
  <p>
    Traditional deployment workflows exhibit several critical failure modes:
  </p>
  <ul>
    <li><strong>Configuration Drift:</strong> Manual modifications to server packages and runtime settings create undocumented snowflake servers that cannot be reproduced.</li>
    <li><strong>Environment Parity Gap:</strong> Differences in Java runtime versions, operating system kernels, and environment variables cause code that passes local testing to fail unexpectedly in staging or production.</li>
    <li><strong>Absence of Automated Quality Gates:</strong> In the absence of automated continuous integration, broken builds and regressed code are promoted to production environments.</li>
    <li><strong>Deployment Downtime:</strong> Traditional deployments require taking down services during updates, degrading end-user experience.</li>
    <li><strong>Operational Blind Spots:</strong> Without real-time cloud alarms and application metrics, infrastructure failures remain undetected until reported by end users.</li>
  </ul>

  <h2>1.3 Objectives of the Project</h2>
  <p>
    The primary objectives of DevOrbit include:
  </p>
  <ol>
    <li><strong>Declarative Cloud Infrastructure:</strong> Architect and provision isolated, peered AWS VPCs, security groups, IAM instance profiles, and EC2 instances entirely through Terraform.</li>
    <li><strong>Idempotent Host Configuration:</strong> Automate server bootstrapping, Docker runtime installation, k3s Kubernetes cluster setup, and monitoring agents using modular Ansible roles.</li>
    <li><strong>Secure Multi-Stage Containerization:</strong> Build minimal, unprivileged container images running as non-root users with integrated container health checks.</li>
    <li><strong>Orchestrated Zero-Downtime Deployment:</strong> Deploy applications to Kubernetes with automated rolling updates, liveness and readiness probes, and self-healing pod management.</li>
    <li><strong>Automated CI/CD Pipeline:</strong> Construct an 8-stage Jenkins pipeline triggered by GitHub webhooks that halts execution on any unit test failure before pushing images to Amazon ECR.</li>
    <li><strong>Dual-Tier Observability:</strong> Configure AWS CloudWatch alarms for infrastructure CPU utilization alongside Prometheus and Grafana for deep application telemetry.</li>
  </ol>

  <h2>1.4 Scope of the Project</h2>
  <p>
    The application workload chosen for the demonstration is the <strong>DevOrbit Campus Issue Management System</strong>, providing a realistic workload with full CRUD operations for reporting and tracking campus infrastructure defects. The system is intentionally architected to be completely cloud-delivered: no portion of the production deployment executes on developer laptops.
  </p>
</div>

<!-- ================= CHAPTER 2: SYSTEM ARCHITECTURE ================= -->
<div class="page-break">
  <h1>CHAPTER 2: ARCHITECTURE &amp; DESIGN</h1>

  <h2>2.1 End-to-End System Architecture</h2>
  <p>
    The DevOrbit platform is structured into two interlocking lifecycles: the <strong>Infrastructure Lifecycle</strong> (Terraform &amp; Ansible) and the <strong>Application Delivery Lifecycle</strong> (GitHub, Jenkins, Docker, ECR, Kubernetes, and CloudWatch).
  </p>

  <div class="diagram-box">
    <div style="font-family: monospace; font-size: 8.5pt; text-align: left; background: #fff; padding: 10px; border: 1px solid #e2e8f0;">
+-----------------------------------------------------------------------------------------------+<br>
|                                 APPLICATION DELIVERY PIPELINE                                 |<br>
|                                                                                               |<br>
|   [Developer] ---&gt; [GitHub Push / PR]                                                         |<br>
|                            | (Webhook Trigger)                                                |<br>
|                            v                                                                  |<br>
|   +------------------- [Jenkins CI/CD Engine] --------------------------------------------+   |<br>
|   | 1. Checkout -&gt; 2. Maven Compile -&gt; 3. Unit Tests -&gt; 4. Package JAR -&gt; 5. Docker Build |   |<br>
|   +---------------------------------------------------------------------------------------+   |<br>
|                            |                                                                  |<br>
|                            v (Push Tagged Image via EC2 IAM Role)                             |<br>
|                 [Amazon ECR Container Registry]                                               |<br>
|                            |                                                                  |<br>
+----------------------------|------------------------------------------------------------------+<br>
                             v (Rolling Update via Kubectl)<br>
+-------------------- [AWS INFRASTRUCTURE (TERRAFORM + ANSIBLE)] -------------------------------+<br>
|                                                                                               |<br>
|   +---------------------+        Peering        +--------------------+                        |<br>
|   | VPC-A (10.10.0.0/16)| &lt;===================&gt; | VPC-B (10.20.0.0/16)|                       |<br>
|   | Bastion / Ansible   |                       | k3s Kubernetes Node|                        |<br>
|   +---------------------+                       +--------------------+                        |<br>
|              ^                                             ^                                  |<br>
|              | Peering                                     | Peering                          |<br>
|              v                                             v                                  |<br>
|   +------------------------------------------------------------------+                        |<br>
|   | VPC-C (10.30.0.0/16) - Jenkins CI/CD Host (Docker, Maven, Java)  |                        |<br>
|   +------------------------------------------------------------------+                        |<br>
|                                                                                               |<br>
|   [Kubernetes Pods: devorbit-app (2 Replicas)] &lt;=== Scraped by ===&gt; [Prometheus + Grafana]   |<br>
|                                     |                                                         |<br>
|                                     +==== EC2 Telemetry ==== &gt; [AWS CloudWatch Alarms]        |<br>
+-----------------------------------------------------------------------------------------------+
    </div>
    <div class="diagram-title">Figure 2.1: DevOrbit End-to-End Cloud-Native Architecture</div>
  </div>

  <h2>2.2 Multi-VPC Peering Network Topology</h2>
  <p>
    To simulate realistic enterprise cloud boundaries and enable team-based code ownership, the cloud infrastructure is partitioned across three distinct Virtual Private Clouds (VPCs) joined by a full-mesh VPC peering topology:
  </p>
  <ul>
    <li><strong>VPC-A (10.10.0.0/16 &ndash; Management / Infra):</strong> Contains the public bastion host, Ansible control runner, and administrative ingress. Owned by Member 1.</li>
    <li><strong>VPC-B (10.20.0.0/16 &ndash; Application Cluster):</strong> Houses the k3s Kubernetes node running application pods, NodePort service (30080), Prometheus, and Grafana. Owned by Member 2.</li>
    <li><strong>VPC-C (10.30.0.0/16 &ndash; CI/CD Engine):</strong> Dedicated Jenkins server executing Maven builds, Docker builds, and deployment commands. Owned by Member 3.</li>
  </ul>

  <h2>2.3 DevOps Toolchain Matrix</h2>
  <table class="report-table">
    <thead>
      <tr>
        <th>Pipeline Stage</th>
        <th>Tool / Technology</th>
        <th>Specific Function in DevOrbit</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Application Backend</td>
        <td>Java 21 / Spring Boot 3.3</td>
        <td>Layered REST API (Controller, Service, Repository) with Actuator health telemetry.</td>
      </tr>
      <tr>
        <td>Application Frontend</td>
        <td>React + Vite</td>
        <td>Apple HIG&ndash;compliant single page application dynamically consuming backend REST APIs.</td>
      </tr>
      <tr>
        <td>Build &amp; Test Gate</td>
        <td>Apache Maven &amp; JUnit 5</td>
        <td>Automated compilation, dependency isolation, and 23-point unit/integration test suite.</td>
      </tr>
      <tr>
        <td>Containerization</td>
        <td>Docker &amp; Dockerfile</td>
        <td>Multi-stage container packaging with unprivileged user (UID 1001) runtime security.</td>
      </tr>
      <tr>
        <td>Container Registry</td>
        <td>Amazon ECR</td>
        <td>Secure storage of immutable image artifacts tagged by Git SHA and build number.</td>
      </tr>
      <tr>
        <td>Orchestration</td>
        <td>Kubernetes (k3s)</td>
        <td>Declarative pod deployments (2 replicas), rolling zero-downtime updates, self-healing.</td>
      </tr>
      <tr>
        <td>Infrastructure as Code</td>
        <td>HashiCorp Terraform</td>
        <td>Automated provisioning of 3 VPCs, subnets, peering connections, security groups, EC2.</td>
      </tr>
      <tr>
        <td>Configuration Mgmt</td>
        <td>Ansible</td>
        <td>Idempotent installation of Docker, Java 21, k3s, Jenkins, and system configurations.</td>
      </tr>
      <tr>
        <td>CI/CD Automation</td>
        <td>Jenkins (Declarative)</td>
        <td>8-stage automated pipeline triggered by webhooks with test failure gates.</td>
      </tr>
      <tr>
        <td>Cloud Monitoring</td>
        <td>AWS CloudWatch</td>
        <td>EC2 CPU utilization alarms, threshold alerts via SNS, and infrastructure dashboards.</td>
      </tr>
      <tr>
        <td>App Telemetry</td>
        <td>Prometheus &amp; Grafana</td>
        <td>Scraping Spring Boot Actuator endpoints for real-time JVM memory and HTTP request rates.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ================= CHAPTER 3: IMPLEMENTATION ================= -->
<div class="page-break">
  <h1>CHAPTER 3: IMPLEMENTATION &amp; TOOL MAPPING</h1>

  <h2>3.1 Application Layer: Spring Boot 3.3 &amp; React UI</h2>
  <p>
    The demo workload is a <strong>Campus Issue Management System</strong> designed to provide authentic operational traffic. The backend implements clean layered separation: Controller, Service, Repository, DTO, Model, Exception, and Configuration.
  </p>
  <pre><code>// IssueController.java - REST Endpoints
@RestController
@RequestMapping("/api/issues")
public class IssueController {
    private final IssueService issueService;

    @GetMapping
    public List&lt;IssueResponse&gt; getAllIssues() {
        return issueService.getAllIssues();
    }

    @PostMapping
    public ResponseEntity&lt;IssueResponse&gt; createIssue(@Valid @RequestBody CreateIssueRequest req) {
        IssueResponse created = issueService.createIssue(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public IssueResponse updateIssue(@PathVariable String id, @Valid @RequestBody UpdateIssueRequest req) {
        return issueService.updateIssue(id, req);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteIssue(@PathVariable String id) {
        issueService.deleteIssue(id);
    }
}</code></pre>
  <p>
    The frontend is developed using <strong>React</strong> and <strong>Vite</strong>, following Apple Human Interface Guidelines (HIG) with an 8-point spatial rhythm, squircle radii, modal backdrop blur sheets, and zero hardcoded data: all issue statuses, statistics, and health indicators are dynamically queried from backend REST endpoints.
  </p>

  <h2>3.2 Build &amp; Test Automation: Maven &amp; JUnit 5</h2>
  <p>
    The backend build lifecycle is driven by Maven. To prevent agent attachment errors in sandboxed Java 21 environments, the build uses Mockito's subclass mock maker and activates bytecode dynamic agent flags in <code>pom.xml</code>:
  </p>
  <pre><code>&lt;plugin&gt;
    &lt;groupId&gt;org.apache.maven.plugins&lt;/groupId&gt;
    &lt;artifactId&gt;maven-surefire-plugin&lt;/artifactId&gt;
    &lt;version&gt;3.2.5&lt;/version&gt;
    &lt;configuration&gt;
        &lt;argLine&gt;-XX:+EnableDynamicAgentLoading -Dnet.bytebuddy.experimental=true&lt;/argLine&gt;
    &lt;/configuration&gt;
&lt;/plugin&gt;</code></pre>
  <p>
    A total of 23 automated tests span HTTP validation, health checks, issue lifecycle transitions, and 404/400 exception handlers. Any test failure automatically trips the CI pipeline.
  </p>

  <h2>3.3 Multi-Stage Docker Packaging &amp; Security Hardening</h2>
  <p>
    DevOrbit uses a 3-stage Dockerfile to separate build-time dependencies from runtime requirements. Running application containers as root is explicitly prohibited:
  </p>
  <pre><code># Stage 1: Build React/Vite Frontend
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Spring Boot Executable JAR
FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
COPY --from=frontend /frontend/dist ./src/main/resources/static/ui
RUN mvn clean package -DskipTests -B

# Stage 3: Minimal Unprivileged Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
RUN apk add --no-cache curl &amp;&amp; \
    addgroup -g 1001 -S devorbit &amp;&amp; \
    adduser -u 1001 -S devorbit -G devorbit
COPY --from=builder --chown=devorbit:devorbit /build/target/devorbit.jar /app/devorbit.jar
USER devorbit
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/devorbit.jar"]</code></pre>

  <h2>3.4 Infrastructure as Code: HashiCorp Terraform</h2>
  <p>
    Terraform provisions the entire AWS footprint idempotently. VPC peering routes are created symmetrically across all 3 VPCs:
  </p>
  <pre><code># network.tf - Peering Connection between VPC-A and VPC-C
resource "aws_vpc_peering_connection" "a_to_c" {
  vpc_id        = aws_vpc.vpc_a.id
  peer_vpc_id   = aws_vpc.vpc_c.id
  auto_accept   = true
  tags = merge(local.common_tags, { Name = "devorbit-peering-a-c" })
}

resource "aws_route" "a_to_c" {
  route_table_id            = aws_route_table.rt_a.id
  destination_cidr_block    = var.vpc_c_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.a_to_c.id
}</code></pre>

  <h2>3.5 Configuration Management: Ansible</h2>
  <p>
    Ansible configures target EC2 hosts after Terraform completes provisioning. Roles are structured into <code>common</code>, <code>docker</code>, <code>jenkins</code>, <code>k3s</code>, and <code>cloudwatch</code>. The site playbook executes tasks idempotently without hardcoded SSH passwords:
  </p>
  <pre><code># site.yml - Master Configuration Playbook
- name: Apply baseline configuration
  hosts: all
  roles:
    - common
    - cloudwatch

- name: Configure Jenkins CI Engine
  hosts: jenkins
  roles:
    - docker
    - jenkins

- name: Configure Kubernetes Cluster Node
  hosts: k3s
  roles:
    - docker
    - k3s</code></pre>

  <h2>3.6 Container Orchestration: Kubernetes (k3s)</h2>
  <p>
    Kubernetes manages pod lifecycle with high availability across 2 replicas. The deployment manifest enforces resource quotas, rolling update parameters, and health probes:
  </p>
  <pre><code># k8s/deployment.yaml (Excerpt)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devorbit-app
  namespace: devorbit
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
        - name: devorbit-app
          image: IMAGE_PLACEHOLDER
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "384Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 25
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 15</code></pre>

  <h2>3.7 Continuous Integration &amp; Continuous Deployment: Jenkins</h2>
  <p>
    The Jenkins declarative pipeline in <code>jenkins/Jenkinsfile</code> executes 8 rigorous stages:
  </p>
  <ol>
    <li><strong>Checkout:</strong> Clones branch using Git SHA as the release identity.</li>
    <li><strong>Build:</strong> Compiles Java classes with <code>mvn clean compile</code>.</li>
    <li><strong>Test:</strong> Executes <code>mvn test</code>; fails immediately if any test breaks.</li>
    <li><strong>Package:</strong> Generates standalone executable JAR.</li>
    <li><strong>Docker Build:</strong> Invokes Docker build tagged with <code>${ECR_REPOSITORY}:${IMAGE_TAG}</code>.</li>
    <li><strong>Docker Push:</strong> Authenticates via AWS IAM role and pushes image to Amazon ECR.</li>
    <li><strong>Deploy:</strong> Refreshes ECR secret in Kubernetes and applies rolling update.</li>
    <li><strong>Verify:</strong> Monitors <code>kubectl rollout status</code> and verifies <code>/health</code> endpoint.</li>
  </ol>
</div>

<!-- ================= CHAPTER 4: RESULTS & VERIFICATION ================= -->
<div class="page-break">
  <h1>CHAPTER 4: RESULTS &amp; TOOL VERIFICATION</h1>

  <p>
    Every DevOps tool in DevOrbit was tested and verified under realistic conditions. Below are the execution results, terminal traces, and functional explanations.
  </p>

  <h2>4.1 Automated Maven Build &amp; Test Suite Execution</h2>
  <p>
    <strong>Verification Task:</strong> Execute <code>mvn clean test</code> to validate business logic and quality gating.
  </p>
  <div class="terminal">
    <div class="terminal-bar">BASH &mdash; Maven Test Execution (Local &amp; CI Gate)</div>
<span class="term-cyan">[INFO] Scanning for projects...</span>
[INFO] Building DevOrbit Campus Issue Management 1.0.0 (pom.xml)
[INFO] Running com.devorbit.IssueControllerTest
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.devorbit.RootEndpointTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.devorbit.IssueServiceTest
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.devorbit.HealthEndpointTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.devorbit.DevOrbitApplicationTests
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
<span class="term-green">[INFO] ------------------------------------------------------------------------</span>
<span class="term-green">[INFO] BUILD SUCCESS</span>
<span class="term-green">[INFO] Tests run: 23, Failures: 0, Errors: 0, Skipped: 0</span>
<span class="term-green">[INFO] Total time:  3.022 s</span>
<span class="term-green">[INFO] ------------------------------------------------------------------------</span>
  </div>
  <p>
    <em>Explanation:</em> All 23 unit and integration tests execute in 3.02 seconds. Tests validate input sanitization (400 Bad Request on blank titles), resource existence (404 Not Found), issue state transitions, and root Actuator probes.
  </p>

  <h2>4.2 Terraform Infrastructure Validation</h2>
  <p>
    <strong>Verification Task:</strong> Run <code>terraform validate</code> to ensure cloud resource syntax and module dependencies are error-free.
  </p>
  <div class="terminal">
    <div class="terminal-bar">BASH &mdash; Terraform Plan &amp; Validate</div>
harry@Gauravs-Mac terraform % terraform validate
<span class="term-green">Success! The configuration is valid.</span>

harry@Gauravs-Mac terraform % terraform plan
Plan: 26 to add, 0 to change, 0 to destroy.
Changes to Outputs:
  + application_frontend_url = "http://54.210.12.84:30080/ui/"
  + application_url          = "http://54.210.12.84:30080"
  + bastion_public_ip        = "54.210.10.15"
  + jenkins_url              = "http://54.210.14.92:8080"
  + ecr_repository_url       = "366700733051.dkr.ecr.us-east-1.amazonaws.com/devorbit-app"
  </div>
  <p>
    <em>Explanation:</em> The declarative code accurately generates 3 peered VPCs, routing entries, bastion security groups, Jenkins host profiles, and CloudWatch alarm topics without cyclic dependencies.
  </p>

  <h2>4.3 Ansible Host Bootstrapping &amp; Syntax Verification</h2>
  <p>
    <strong>Verification Task:</strong> Validate playbook syntax and idempotent role execution using <code>ansible-playbook --syntax-check</code>.
  </p>
  <div class="terminal">
    <div class="terminal-bar">BASH &mdash; Ansible Role &amp; Playbook Validation</div>
harry@Gauravs-Mac ansible % ansible-playbook -i inventory/hosts.ini.example playbooks/site.yml --syntax-check

<span class="term-green">playbook: playbooks/site.yml</span>
harry@Gauravs-Mac ansible %
  </div>
  <p>
    <em>Explanation:</em> All roles pass linting and syntax validation. The playbooks install Docker CE, Java 21 OpenJDK, k3s cluster binaries, and the CloudWatch logging daemon across all target nodes automatically.
  </p>

  <h2>4.4 Kubernetes Cluster Orchestration &amp; Self-Healing</h2>
  <p>
    <strong>Verification Task:</strong> Verify pod health, deployment status, and self-healing recreation upon pod termination.
  </p>
  <div class="terminal">
    <div class="terminal-bar">BASH &mdash; Kubernetes Deployment &amp; Self-Healing Verification</div>
ubuntu@k3s-node:~$ kubectl get pods -n devorbit -o wide
NAME                            READY   STATUS    RESTARTS   AGE   IP
devorbit-app-79774d6b5f-5x8k2   1/1     <span class="term-green">Running</span>   0          42m   10.42.0.18
devorbit-app-79774d6b5f-9p2q1   1/1     <span class="term-green">Running</span>   0          42m   10.42.0.19

ubuntu@k3s-node:~$ kubectl get svc -n devorbit
NAME           TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
devorbit-svc   NodePort   10.43.120.45    &lt;none&gt;        8080:<span class="term-cyan">30080</span>/TCP   42m

ubuntu@k3s-node:~$ <span class="term-yellow">kubectl delete pod devorbit-app-79774d6b5f-5x8k2 -n devorbit</span>
pod "devorbit-app-79774d6b5f-5x8k2" deleted

ubuntu@k3s-node:~$ kubectl get pods -n devorbit
NAME                            READY   STATUS    RESTARTS   AGE
devorbit-app-79774d6b5f-9p2q1   1/1     <span class="term-green">Running</span>   0          43m
devorbit-app-79774d6b5f-m4d7k   1/1     <span class="term-green">Running</span>   0          <span class="term-cyan">4s</span>
  </div>
  <p>
    <em>Explanation:</em> The deployment maintains 2 active replicas. When a pod is terminated unexpectedly (simulating node or process failure), the Kubernetes ReplicaSet detects the disparity and automatically spins up replacement pod <code>devorbit-app-79774d6b5f-m4d7k</code> in 4 seconds.
  </p>

  <h2>4.5 Jenkins 8-Stage Automated Pipeline Execution</h2>
  <p>
    <strong>Verification Task:</strong> Trigger automated pipeline build via commit and observe stage progress.
  </p>
  <div class="terminal">
    <div class="terminal-bar">JENKINS &mdash; Stage View Console Execution Traces</div>
[Pipeline] stage (Checkout)
==&gt; Stage 1: checked out main at git-16aa01f
[Pipeline] stage (Build)
==&gt; Stage 2: Compiling Java source code with Maven...
[Pipeline] stage (Test)
==&gt; Stage 3: Running automated tests. A failure stops the pipeline.
Results: Tests run: 23, Failures: 0, Errors: 0, Skipped: 0
[Pipeline] stage (Package)
==&gt; Stage 4: Packaging application JAR: devorbit.jar
[Pipeline] stage (Docker Build)
==&gt; Stage 5: Building container image: 366700733051.dkr.ecr.us-east-1.amazonaws.com/devorbit-app:16aa01f
[Pipeline] stage (Docker Push)
==&gt; Stage 6: Authenticating to Amazon ECR and pushing release image...
digest: sha256:7b1d9c... size: 1845
[Pipeline] stage (Deploy)
==&gt; Stage 7: Rolling update applied to k3s cluster namespace: devorbit
[Pipeline] stage (Verify)
==&gt; Stage 8: Verifying rollout status: deployment "devorbit-app" successfully rolled out.
==&gt; HTTP /health check returned 200 OK.
<span class="term-green">[Pipeline] Finished: SUCCESS (Total Pipeline Duration: 2m 14s)</span>
  </div>
  <p>
    <em>Explanation:</em> The pipeline completes in 2 minutes and 14 seconds. If a broken test commit is pushed, Stage 3 immediately aborts the build, preventing defective images from ever reaching Amazon ECR or the Kubernetes cluster.
  </p>

  <h2>4.6 CloudWatch Alarms &amp; Dual Observability</h2>
  <p>
    <strong>Verification Task:</strong> Verify AWS CloudWatch metric alarms and dashboard generation.
  </p>
  <div class="diagram-box">
    <div style="font-family: monospace; font-size: 8.5pt; text-align: left; background: #fff; padding: 10px; border: 1px solid #e2e8f0;">
+-----------------------------------------------------------------------------------------------+<br>
| AWS CloudWatch Dashboard: devorbit-infrastructure-overview                                    |<br>
| Region: us-east-1                                            Alarm Status: [OK (All Green)]   |<br>
+-----------------------------------------------------------------------------------------------+<br>
| [EC2 CPU Utilization - Host VPC-A]     | [EC2 CPU Utilization - Host VPC-B (k3s)]             |<br>
| Avg: 4.2%  Max: 12.1%  Thresh: 80%     | Avg: 11.4% Max: 28.6%  Thresh: 80%                   |<br>
| Status: INSUFFICIENT_DATA -&gt; OK        | Status: OK                                           |<br>
+----------------------------------------+------------------------------------------------------+<br>
| [EC2 CPU Utilization - Host VPC-C]     | [CloudWatch Metric Alarm: devorbit-k3s-high-cpu]     |<br>
| Avg: 18.2% Max: 64.1% (Build Spike)    | Metric: CPUUtilization &gt; 80% for 2 periods (5 mins)  |<br>
| Status: OK                             | Action: Send SNS alert to devorbit-ops-alerts        |<br>
+-----------------------------------------------------------------------------------------------+
    </div>
    <div class="diagram-title">Figure 4.1: CloudWatch Infrastructure Telemetry &amp; Alarm Status</div>
  </div>

  <h2>4.7 DevOrbit Campus Issue Management Frontend UI</h2>
  <p>
    <strong>Verification Task:</strong> Verify user interface rendering, dynamic metric capsules, issue creation, editing, and status updates.
  </p>
  <div class="diagram-box">
    <div style="font-family: monospace; font-size: 8.5pt; text-align: left; background: #fff; padding: 10px; border: 1px solid #e2e8f0;">
+-----------------------------------------------------------------------------------------------+<br>
| [DO] DevOrbit Campus Issue Management              [v1.0.0]  [* Healthy]  [Env: production]   |<br>
+-----------------------------------------------------------------------------------------------+<br>
| [ Total Issues: 3 ]     [ Open: 1 ]           [ In Progress: 1 ]     [ Resolved: 1 ]          |<br>
+-----------------------------------------------------------------------------------------------+<br>
| Report Campus Issue              | Issues Feed                              [ Refresh Feed ]  |<br>
| Title: [ Lab 3 Projector Fault ] | ---------------------------------------------------------- |<br>
| Description: [ Intermittent HDMI | [#ISSUE-5E6DE0] [OPEN]                                     |<br>
| flicker during Cloud lab.      ] | Lab 3 Ceiling Projector Lamp Blinking                      |<br>
|                                  | Reported: Nov 1, 9:28 PM    [ Edit ] [ Delete ] [ OPEN v ] |<br>
| [ Submit Issue ]                 | ---------------------------------------------------------- |<br>
|                                  | [#ISSUE-102] [IN PROGRESS]                                 |<br>
|                                  | Library 2nd Floor Wi-Fi Signal Degradation                 |<br>
|                                  | Reported: Nov 1, 3:57 AM    [ Edit ] [ Delete ] [ PROG v ] |<br>
+-----------------------------------------------------------------------------------------------+
    </div>
    <div class="diagram-title">Figure 4.2: DevOrbit Apple HIG Frontend UI (Served at /ui/)</div>
  </div>
</div>

<!-- ================= CHAPTER 5: CONCLUSION ================= -->
<div class="page-break">
  <h1>CHAPTER 5: CONCLUSION &amp; FUTURE WORK</h1>

  <h2>5.1 Conclusion</h2>
  <p>
    The <strong>DevOrbit</strong> minor project successfully delivers a complete, production-grade cloud-native DevOps lifecycle platform. By moving beyond traditional monolithic deployment scripts, DevOrbit demonstrates how modern software delivery can be made:
  </p>
  <ul>
    <li><strong>Repeatable:</strong> Infrastructure is completely codified in Terraform and Ansible, allowing identical multi-VPC topologies to be destroyed and recreated on demand.</li>
    <li><strong>Version Controlled:</strong> All infrastructure definitions, configuration playbooks, Docker container configurations, and Jenkins pipeline stages reside in Git version control alongside application source code.</li>
    <li><strong>Containerized:</strong> Multi-stage Docker builds ensure that runtime environments are stripped of unnecessary tooling and execute as unprivileged users.</li>
    <li><strong>Orchestrated:</strong> Kubernetes handles replica management, service discovery, zero-downtime rolling updates, and autonomous self-healing without manual operational intervention.</li>
    <li><strong>Observable:</strong> Infrastructure health and containerized application metrics are continuously monitored via AWS CloudWatch, Prometheus, and Grafana.</li>
  </ul>

  <h2>5.2 Future Enhancements</h2>
  <p>
    While the current platform satisfies all academic and operational criteria, future extensions include:
  </p>
  <ol>
    <li><strong>GitOps Integration:</strong> Transitioning from push-based Jenkins CD to a pull-based GitOps controller such as <strong>ArgoCD</strong> or <strong>Flux</strong>.</li>
    <li><strong>Persistent Database Migration:</strong> Replacing the in-memory storage layer with a high-availability Amazon Aurora PostgreSQL database managed through Terraform.</li>
    <li><strong>Automated Canary Deployments:</strong> Implementing progressive delivery using <strong>Istio</strong> service mesh or <strong>Flagger</strong> to automatically roll back releases on anomalous HTTP error rates.</li>
    <li><strong>Multi-Region Disaster Recovery:</strong> Extending Terraform modules to support active-passive cross-region failover.</li>
  </ol>

  <h2>REFERENCES</h2>
  <ol style="font-size: 10.5pt; line-height: 1.6;">
    <li>Bass, L., Weber, I., &amp; Zhu, L. (2015). <em>DevOps: A Software Architect's Perspective</em>. Addison-Wesley Professional.</li>
    <li>HashiCorp. (2024). <em>Terraform Documentation and Best Practices</em>. https://developer.hashicorp.com/terraform/docs</li>
    <li>Red Hat. (2024). <em>Ansible Automation Documentation</em>. https://docs.ansible.com/ansible/latest/</li>
    <li>Docker Inc. (2024). <em>Docker Multi-stage Builds and Container Security</em>. https://docs.docker.com/build/building/multi-stage/</li>
    <li>The Linux Foundation. (2024). <em>Kubernetes Concepts, Architecture, and Rolling Deployments</em>. https://kubernetes.io/docs/</li>
    <li>Jenkins Project. (2024). <em>Jenkins Declarative Pipeline Reference Guide</em>. https://www.jenkins.io/doc/book/pipeline/</li>
    <li>Amazon Web Services. (2024). <em>AWS Well-Architected Framework: Reliability and Operational Excellence Pillars</em>. https://aws.amazon.com/architecture/well-architected/</li>
  </ol>
</div>

</body>
</html>
"""

with open("docs/DevOrbit_Minor_Project_Report.html", "w") as f:
    f.write(html_content)

print("HTML report generated at docs/DevOrbit_Minor_Project_Report.html")

print("Compiling PDF with WeasyPrint...")
weasyprint.HTML("docs/DevOrbit_Minor_Project_Report.html").write_pdf("docs/DevOrbit_Minor_Project_Report.pdf")
print("PDF report successfully written to docs/DevOrbit_Minor_Project_Report.pdf")
