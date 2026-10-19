# ------------------------------------------------------------------------------
# DevOrbit Terraform outputs
# Feed these values into the Ansible inventory and the Jenkins credentials.
# ------------------------------------------------------------------------------

output "vpc_ids" {
  description = "VPC identifier for each DevOrbit network"
  value       = { for name, vpc in aws_vpc.this : name => vpc.id }
}

output "public_subnet_ids" {
  description = "Public subnet identifier for each VPC"
  value       = { for name, subnet in aws_subnet.public : name => subnet.id }
}

output "security_group_ids" {
  description = "Security group identifier for each VPC"
  value = {
    infra = aws_security_group.infra.id
    app   = aws_security_group.app.id
    ci    = aws_security_group.ci.id
  }
}

output "vpc_peering_connection_ids" {
  description = "VPC peering connection identifiers (full mesh)"
  value       = { for name, pcx in aws_vpc_peering_connection.this : name => pcx.id }
}

output "instance_ids" {
  description = "EC2 instance identifier for each DevOrbit host"
  value       = { for name, instance in local.instances : name => instance.id }
}

output "public_ips" {
  description = "Public IPv4 address for each DevOrbit host"
  value       = { for name, instance in local.instances : name => instance.public_ip }
}

output "private_ips" {
  description = "Private IPv4 address for each DevOrbit host"
  value       = { for name, instance in local.instances : name => instance.private_ip }
}

output "ssh_commands" {
  description = "SSH commands for each host (replace the private key path)"
  value = {
    for name, instance in local.instances :
    name => "ssh -i <YOUR_PRIVATE_KEY.pem> ubuntu@${instance.public_ip}"
  }
}

output "ansible_inventory" {
  description = "Ready to paste Ansible inventory values"
  value = {
    bastion_public_ip = var.enable_bastion ? aws_instance.bastion[0].public_ip : ""
    jenkins_public_ip = aws_instance.jenkins.public_ip
    k3s_public_ip     = aws_instance.app.public_ip
    k3s_private_ip    = aws_instance.app.private_ip
  }
}

output "jenkins_url" {
  description = "Jenkins web UI URL"
  value       = "http://${aws_instance.jenkins.public_ip}:8080"
}

output "application_url" {
  description = "DevOrbit REST API URL through the Kubernetes NodePort"
  value       = "http://${aws_instance.app.public_ip}:30080"
}

output "application_frontend_url" {
  description = "DevOrbit React UI URL through the Kubernetes NodePort"
  value       = "http://${aws_instance.app.public_ip}:30080/ui/"
}

output "ecr_repository_name" {
  description = "ECR repository name used by the Jenkins pipeline"
  value       = aws_ecr_repository.app.name
}

output "ecr_repository_url" {
  description = "ECR repository URL used by the Jenkins pipeline"
  value       = aws_ecr_repository.app.repository_url
}

output "sns_topic_arn" {
  description = "SNS topic that CloudWatch alarms publish to"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for host/system logs"
  value       = aws_cloudwatch_log_group.system.name
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL for the DevOrbit team"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "kubeconfig_hint" {
  description = "How to fetch the k3s kubeconfig for the Jenkins credential"
  value       = "On the k3s host run: sudo cat /etc/rancher/k3s/k3s.yaml, replace 127.0.0.1 with ${aws_instance.app.private_ip}, then upload the file to Jenkins as a Secret file credential named k8s-kubeconfig."
}
