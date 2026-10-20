# ------------------------------------------------------------------------------
# Remote state backend for the DevOrbit main stack.
#
# The bucket and lock table are created once by terraform/bootstrap.
# All team members should run `terraform init` before planning or applying.
# ------------------------------------------------------------------------------

terraform {
  backend "s3" {
    bucket       = "devorbit-tfstate-366700733051"
    key          = "devorbit/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
