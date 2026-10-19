# ------------------------------------------------------------------------------
# Shared local values (naming, network map, peering map, instance map).
# Owner: Member 1 (Cloud/Infra)
# ------------------------------------------------------------------------------

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  az          = data.aws_availability_zones.available.names[0]

  vpcs = {
    infra = {
      cidr    = var.vpc_cidrs.infra
      subnet  = var.subnet_cidrs.infra
      purpose = "management"
    }
    app = {
      cidr    = var.vpc_cidrs.app
      subnet  = var.subnet_cidrs.app
      purpose = "application"
    }
    ci = {
      cidr    = var.vpc_cidrs.ci
      subnet  = var.subnet_cidrs.ci
      purpose = "cicd"
    }
  }

  peerings = {
    "infra-app" = { a = "infra", b = "app" }
    "infra-ci"  = { a = "infra", b = "ci" }
    "app-ci"    = { a = "app", b = "ci" }
  }

  peer_routes = merge([
    for name, p in local.peerings : {
      "${name}-${p.a}-to-${p.b}" = {
        route_table = p.a
        destination = local.vpcs[p.b].cidr
        peering     = name
      }
      "${name}-${p.b}-to-${p.a}" = {
        route_table = p.b
        destination = local.vpcs[p.a].cidr
        peering     = name
      }
    }
  ]...)

  # Convenience map used by monitoring.tf and outputs.tf.
  instances = merge(
    {
      jenkins = aws_instance.jenkins
      app     = aws_instance.app
    },
    {
      for index, instance in aws_instance.bastion :
      (index == 0 ? "bastion" : "bastion-${index + 1}") => instance
    }
  )
}
