import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # Set 16:9 widescreen format
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    NAVY = RGBColor(10, 25, 47)         # #0A192F
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(248, 250, 252)  # #F8FAFC
    CARD_BORDER = RGBColor(226, 232, 240)
    CARD_BG = RGBColor(255, 255, 255)
    TEXT_DARK = RGBColor(15, 23, 42)    # #0F172A
    TEXT_MUTED = RGBColor(100, 116, 139)# #64748B
    PRIMARY_BLUE = RGBColor(14, 116, 144) # #0E7490
    ACCENT_BLUE = RGBColor(2, 132, 199)   # #0284C7
    EMERALD = RGBColor(16, 185, 129)     # #10B981

    def add_header(slide, title_text, category_text="DEVORBIT - DEVOPS AUTOMATION PLATFORM"):
        # Header background banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE
        p_cat.space_after = Pt(4)

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        return shape

    # ==================== SLIDE 1: TITLE SLIDE ====================
    slide1 = prs.slides.add_slide(blank_layout)
    # Background
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "DEPARTMENT OF NETWORKING AND COMMUNICATIONS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    p = tf1.add_paragraph()
    p.text = "DEVORBIT"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "A Cloud-Native DevOps Lifecycle Platform for Repeatable and Observable Delivery"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Presented by:\nGAURAV (Member 3 - CI/CD & Observability) & Team Members\nDepartment of Networking and Communications | SRMIST KTR"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.line_spacing = 1.3

    # ==================== SLIDE 2: ABSTRACT & PROBLEM STATEMENT ====================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Executive Summary & Problem Statement")

    # Left Card: Traditional Delivery Problems
    create_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_prob = slide2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_prob = tb_prob.text_frame
    tf_prob.word_wrap = True
    p = tf_prob.paragraphs[0]
    p.text = "THE PROBLEM: FRAGILE MANUAL DELIVERY"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(220, 38, 38)
    p.space_after = Pt(14)

    problems = [
        ("Configuration Drift", "Manual server packages and undocumented OS changes create snowflake environments that cannot be recreated."),
        ("Environment Parity Gap", "'It works on my machine' syndrome caused by differing Java versions, kernels, and missing dependencies."),
        ("No Quality Gates", "Absence of automated continuous testing allows defective code to be promoted into active production."),
        ("Deployment Downtime", "Manual service restarts and direct server updates force application downtime during releases."),
        ("Operational Blind Spots", "Lack of automated telemetry and alarms leaves teams unaware of resource spikes or server failures.")
    ]
    for title, desc in problems:
        p = tf_prob.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # Right Card: The DevOrbit Solution
    create_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_sol = slide2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf_sol = tb_sol.text_frame
    tf_sol.word_wrap = True
    p = tf_sol.paragraphs[0]
    p.text = "THE DEVORBIT SOLUTION: 5 CORE PILLARS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p.space_after = Pt(14)

    solutions = [
        ("Infrastructure as Code (Terraform)", "Declarative, idempotent provisioning of 3 peered AWS VPCs, security groups, IAM roles, and EC2 instances."),
        ("Configuration Management (Ansible)", "Automated host setup installing Docker CE, Java 21 OpenJDK, k3s cluster, and CloudWatch agent."),
        ("Multi-Stage Containerization (Docker)", "Unprivileged, non-root runtime container (UID 1001) packaging Spring Boot backend + React UI."),
        ("Zero-Downtime Orchestration (Kubernetes)", "2-replica deployment on k3s with rolling updates, liveness/readiness probes, and self-healing pods."),
        ("Automated CI/CD & Observability", "8-stage Jenkins pipeline triggered by GitHub webhooks, pushing to Amazon ECR, monitored by CloudWatch.")
    ]
    for title, desc in solutions:
        p = tf_sol.add_paragraph()
        p.text = f"✔ {title}: {desc}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # ==================== SLIDE 3: SYSTEM ARCHITECTURE ====================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "End-to-End System & Multi-VPC Architecture")

    create_card(slide3, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.2))
    tb_arch = slide3.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.1), Inches(4.8))
    tf_arch = tb_arch.text_frame
    tf_arch.word_wrap = True

    p = tf_arch.paragraphs[0]
    p.text = "CLOUD-NATIVE DELIVERY LIFECYCLE ON AMAZON WEB SERVICES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(10)

    arch_text = """
    [Developer Workstation]
              │ (Git Push / PR)
              ▼
    [GitHub Repository] ──────── (Webhook Trigger) ───────► [VPC-C: Jenkins Host (10.30.0.0/16)]
                                                              │ 1. Checkout Git SHA
                                                              │ 2. Maven Compile & Tests (23 Tests)
                                                              │ 3. Build Multi-Stage Docker Image
                                                              ▼
                                                   [Amazon ECR Registry (us-east-1)]
                                                              │
                                       (kubectl rolling deploy│authenticated by EC2 IAM Role)
                                                              ▼
                                                   [VPC-B: k3s Kubernetes Node (10.20.0.0/16)]
                                                              ├── Namespace: devorbit
                                                              ├── Pod 1 & Pod 2 (2 Replicas, Non-Root)
                                                              ├── Probes: /health (Liveness & Readiness)
                                                              └── Service: NodePort (Port 30080)
                                                                      │
                                                ┌─────────────────────┴─────────────────────┐
                                                ▼                                           ▼
                                      [Prometheus + Grafana]                      [AWS CloudWatch Dashboard]
                                    (JVM & HTTP Telemetry)                      (EC2 CPU Metrics & Alarms)
    """
    p = tf_arch.add_paragraph()
    p.text = arch_text
    p.font.size = Pt(9)
    p.font.name = "Courier New"
    p.font.color.rgb = NAVY

    # ==================== SLIDE 4: TOOLCHAIN MATRIX ====================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "DevOps Toolchain Matrix & Team Ownership")

    create_card(slide4, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.2))
    
    # 3 Member Ownership Columns
    owners = [
        ("MEMBER 1: INFRASTRUCTURE & CLOUD", "VPC-A (10.10.0.0/16)", [
            "Terraform: 3 VPCs, subnets, peering, security groups, IAM roles, ECR",
            "Ansible: Baseline 'common' role & CloudWatch daemon role",
            "Bastion Host: Administrative ingress & Ansible control runner",
            "CloudWatch: SNS alert topic, CPU threshold alarms, operational dashboard"
        ]),
        ("MEMBER 2: CONTAINERS & KUBERNETES", "VPC-B (10.20.0.0/16)", [
            "Docker: 3-stage multi-stage build running as non-root user (UID 1001)",
            "Ansible: 'k3s' role installing single-node Kubernetes cluster",
            "Kubernetes Manifests: Namespace, Deployment (2 replicas), NodePort (30080)",
            "Resilience: Pod self-healing, rolling zero-downtime updates, probe checks"
        ]),
        ("MEMBER 3: CI/CD & OBSERVABILITY", "VPC-C (10.30.0.0/16)", [
            "Ansible: 'jenkins' role installing Jenkins LTS, Maven 3.9, Docker CE",
            "Jenkinsfile: 8-stage declarative pipeline with automated quality gate",
            "Amazon ECR: Authenticated image push via attached EC2 IAM instance profile",
            "App Monitoring: Prometheus scraping Spring Boot Actuator + Grafana views"
        ])
    ]

    col_w = Inches(3.65)
    gap = Inches(0.3)
    start_x = Inches(1.05)

    for i, (title, vpc, items) in enumerate(owners):
        card_x = start_x + i * (col_w + gap)
        create_card(slide4, card_x, Inches(2.0), col_w, Inches(4.6), bg_color=LIGHT_BG)
        
        tb = slide4.shapes.add_textbox(card_x + Inches(0.2), Inches(2.15), col_w - Inches(0.4), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = vpc
        p.font.size = Pt(9.5)
        p.font.italic = True
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

        for itm in items:
            p = tf.add_paragraph()
            p.text = f"• {itm}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_DARK
            p.space_after = Pt(6)

    # ==================== SLIDE 5: TERRAFORM & ANSIBLE ====================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Infrastructure as Code & Configuration Management")

    create_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_tf = slide5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_tf = tb_tf.text_frame
    tf_tf.word_wrap = True
    p = tf_tf.paragraphs[0]
    p.text = "HASHICORP TERRAFORM (IaC)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(12)

    tf_pts = [
        ("Multi-VPC Topology", "Provisions VPC-A (10.10.0.0/16), VPC-B (10.20.0.0/16), and VPC-C (10.30.0.0/16) with dedicated subnets and route tables."),
        ("Full-Mesh Peering", "Creates bi-directional peering connections (A-B, B-C, A-C) allowing private IP routing between Jenkins, k3s, and Bastion."),
        ("Least-Privilege IAM", "Attaches EC2 instance profiles allowing Jenkins to push to ECR and k3s to pull without embedding API access keys in code."),
        ("Automated Alarms", "Provisions CloudWatch metric alarms for EC2 CPU utilization (>80%) and SNS notification topics."),
        ("Idempotency", "'terraform validate' and 'plan' guarantee consistent, repeatable deployments without duplicate resources.")
    ]
    for t, d in tf_pts:
        p = tf_tf.add_paragraph()
        p.text = f"✔ {t}: {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    create_card(slide5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_ans = slide5.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf_ans = tb_ans.text_frame
    tf_ans.word_wrap = True
    p = tf_ans.paragraphs[0]
    p.text = "ANSIBLE AUTOMATION (Config Mgmt)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    ans_pts = [
        ("Modular Roles", "Structured into roles/common, roles/docker, roles/jenkins, roles/k3s, and roles/cloudwatch for separation of concerns."),
        ("Idempotent Execution", "Tasks only apply changes when necessary; repeated executions produce zero unintended configuration drift."),
        ("Automated Runtime Setup", "Installs Docker Engine CE, OpenJDK 21, Maven 3.9, and k3s binaries automatically upon EC2 boot."),
        ("No Stored Credentials", "Uses SSH key authentication through bastion host; zero plain-text passwords stored in playbooks."),
        ("Unified Master Playbook", "Running 'site.yml' configures the entire 3-node AWS cluster in one automated pass.")
    ]
    for t, d in ans_pts:
        p = tf_ans.add_paragraph()
        p.text = f"✔ {t}: {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # ==================== SLIDE 6: DOCKER & KUBERNETES ====================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Containerization (Docker) & Orchestration (Kubernetes)")

    create_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_doc = slide6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_doc = tb_doc.text_frame
    tf_doc.word_wrap = True
    p = tf_doc.paragraphs[0]
    p.text = "DOCKER MULTI-STAGE HARDENING"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(12)

    doc_pts = [
        ("Stage 1 (Frontend)", "Node 20 Alpine compiles React/Vite assets into minified production bundles."),
        ("Stage 2 (Backend)", "Maven 3.9 + Temurin JDK 21 compiles Java classes and embeds frontend under /static/ui into a single executable JAR."),
        ("Stage 3 (Runtime)", "Eclipse Temurin 21 JRE Alpine: contains only the minimal JRE runtime (~180MB total size)."),
        ("Non-Root Security", "Creates and enforces unprivileged user 'devorbit' (UID 1001). Root execution is strictly disabled."),
        ("Container Healthcheck", "Integrated Docker HEALTHCHECK queries '/health' every 30s to verify internal JVM availability.")
    ]
    for t, d in doc_pts:
        p = tf_doc.add_paragraph()
        p.text = f"• {t}: {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    create_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_k8s = slide6.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf_k8s = tb_k8s.text_frame
    tf_k8s.word_wrap = True
    p = tf_k8s.paragraphs[0]
    p.text = "KUBERNETES (k3s) ORCHESTRATION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    k8s_pts = [
        ("High Availability Replicas", "Deployment enforces 2 concurrent pod replicas across the cluster."),
        ("Rolling Updates (Zero Downtime)", "RollingUpdate strategy (maxSurge=1, maxUnavailable=0) updates pods one by one without user interruption."),
        ("Self-Healing Pods", "If a pod crashes or is deleted via 'kubectl delete pod', the ReplicaSet recreates it within 4 seconds."),
        ("Readiness & Liveness Probes", "Probes query '/health'. Kubernetes only routes traffic to pods that are verified 'UP' and ready."),
        ("Stable Service Routing", "Exposes pods via NodePort Service on port 30080, decoupling access from ephemeral Pod IPs.")
    ]
    for t, d in k8s_pts:
        p = tf_k8s.add_paragraph()
        p.text = f"• {t}: {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # ==================== SLIDE 7: JENKINS 8-STAGE CI/CD PIPELINE ====================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Continuous Integration & Delivery (The 8 Jenkins Stages)")

    create_card(slide7, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.2))
    
    stages = [
        ("1. Checkout", "Pulls Git commit SHA dynamically as immutable release tag."),
        ("2. Build", "Compiles Java source code cleanly using 'mvn clean compile'."),
        ("3. Automated Test", "Executes 23 unit/integration tests. A single failure STOPS the pipeline."),
        ("4. Package", "Generates production executable JAR with embedded static UI assets."),
        ("5. Docker Build", "Builds hardened multi-stage container tagged with Git SHA."),
        ("6. Docker Push", "Authenticates to Amazon ECR via EC2 IAM role and pushes release image."),
        ("7. K8s Deploy", "Refreshes ECR docker-registry secret and applies rolling update to k3s."),
        ("8. Verification", "Verifies 'rollout status' and queries HTTP '/health' endpoint for 200 OK.")
    ]

    for idx, (st_name, st_desc) in enumerate(stages):
        row = idx // 4
        col = idx % 4
        x = Inches(1.1) + col * Inches(2.8)
        y = Inches(2.0) + row * Inches(2.3)
        
        # Sub-card
        create_card(slide7, x, y, Inches(2.6), Inches(2.1), bg_color=LIGHT_BG)
        tb = slide7.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), Inches(2.3), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = st_name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = st_desc
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    # ==================== SLIDE 8: RESULTS & VERIFICATION ====================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Live Demonstration Results & Test Verification")

    results = [
        ("Automated Tests", "23/23 tests pass locally & in CI (100% pass rate in 3.02s). Halts build if tests fail."),
        ("Terraform Plan", "Valid syntax; provisions 26 resources (3 VPCs, routes, security groups, IAM) with zero drift."),
        ("Ansible Syntax", "Zero linting errors across 5 roles; idempotently configures EC2 instances upon execution."),
        ("Docker Build", "Multi-stage artifact packaging (~180MB) running as non-root user 'devorbit:1001'."),
        ("Kubernetes Healing", "Pod deleted via 'kubectl delete pod'; replacement pod recreated & healthy in 4 seconds."),
        ("Rolling Update", "New version rolled out with zero downtime (maxSurge=1, maxUnavailable=0)."),
        ("CloudWatch Metrics", "EC2 CPU utilization monitored with automated threshold alerts (>80%) via SNS topic."),
        ("React Frontend", "Apple HIG UI served at /ui/ with real-time health badges & full dynamic issue CRUD.")
    ]

    create_card(slide8, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.2))
    
    for idx, (r_title, r_desc) in enumerate(results):
        row = idx // 4
        col = idx % 4
        x = Inches(1.1) + col * Inches(2.8)
        y = Inches(2.0) + row * Inches(2.3)
        
        create_card(slide8, x, y, Inches(2.6), Inches(2.1), bg_color=LIGHT_BG)
        tb = slide8.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), Inches(2.3), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"✔ {r_title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = EMERALD
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = r_desc
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    # ==================== SLIDE 9: CONCLUSION ====================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Conclusion & Academic Takeaways")

    create_card(slide9, Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.8), bg_color=NAVY)
    tb_c = slide9.shapes.add_textbox(Inches(2.0), Inches(2.2), Inches(9.333), Inches(4.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "THE DEVORBIT CORE PHILOSOPHY"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(14)

    p = tf_c.add_paragraph()
    p.text = '"DevOrbit is not merely a CRUD application deployed on AWS;\nit is the entire automated delivery machine revolving around modern DevOps practices."'
    p.font.size = Pt(14)
    p.font.italic = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(20)

    takeaways = [
        "Repeatable: Entire cloud infrastructure provisioned and destroyed deterministically via Terraform & Ansible.",
        "Version Controlled: Every configuration, pipeline step, and Dockerfile resides in Git alongside source code.",
        "Automated: Zero manual SSH or container commands; releases are continuous from Git push to Kubernetes rollout.",
        "Observable: Proactive CloudWatch alerts and Prometheus telemetry provide immediate operational visibility.",
        "Production-Grade: Multi-stage builds, non-root user execution, and rolling zero-downtime deployments."
    ]
    for tk in takeaways:
        p = tf_c.add_paragraph()
        p.text = f"✔ {tk}"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_after = Pt(6)

    # Save presentation
    output_path = "docs/DevOrbit_Project_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully saved to {output_path}")

if __name__ == "__main__":
    create_presentation()
