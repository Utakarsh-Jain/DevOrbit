output "state_bucket_name" {
  description = "S3 bucket that stores the Terraform state file"
  value       = aws_s3_bucket.state.bucket
}

