output "vpc_id" {
  description = "VPC Identifier"
  value       = aws_vpc.devorbit_vpc.id
}

output "public_subnet_id" {
  description = "Public Subnet Identifier"
  value       = aws_subnet.public_subnet.id
}

output "security_group_id" {
  description = "Security Group Identifier"
  value       = aws_security_group.server_sg.id
}

output "instance_id" {
  description = "EC2 Instance Identifier"
  value       = aws_instance.devops_server.id
}

output "public_ip" {
  description = "Public IPv4 address of the DevOrbit EC2 server"
  value       = aws_instance.devops_server.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the provisioned EC2 instance"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.devops_server.public_ip}"
}
