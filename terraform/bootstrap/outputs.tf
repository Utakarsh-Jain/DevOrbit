output "state_bucket_name" {
  description = "S3 bucket that stores the Terraform state file"
  value       = aws_s3_bucket.state.bucket
}

output "lock_table_name" {
  description = "DynamoDB table used for Terraform state locking"
  value       = aws_dynamodb_table.lock.name
}
