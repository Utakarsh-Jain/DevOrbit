# ------------------------------------------------------------------------------
# DevOrbit network layer
# Three VPCs (management/infra, application, CI/CD) connected with VPC peering.
#
#   VPC infra 10.10.0.0/16  -> bastion / management
#   VPC app   10.20.0.0/16  -> k3s cluster and DevOrbit application
#   VPC ci    10.30.0.0/16  -> Jenkins CI/CD host
#
# VPC peering is non-transitive, so all three peering links are created.
# ------------------------------------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

data "aws_caller_identity" "current" {}

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
}

# 1. VPCs
resource "aws_vpc" "this" {
  for_each = local.vpcs

  cidr_block           = each.value.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name    = "${local.name_prefix}-${each.key}-vpc"
    Purpose = each.value.purpose
  }
}

# 2. Public subnets
resource "aws_subnet" "public" {
  for_each = local.vpcs

  vpc_id                  = aws_vpc.this[each.key].id
  cidr_block              = each.value.subnet
  availability_zone       = local.az
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name_prefix}-${each.key}-public-subnet"
  }
}

# 3. Internet gateways
resource "aws_internet_gateway" "this" {
  for_each = local.vpcs

  vpc_id = aws_vpc.this[each.key].id

  tags = {
    Name = "${local.name_prefix}-${each.key}-igw"
  }
}

# 4. Public route tables (internet default route)
resource "aws_route_table" "public" {
  for_each = local.vpcs

  vpc_id = aws_vpc.this[each.key].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this[each.key].id
  }

  tags = {
    Name = "${local.name_prefix}-${each.key}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  for_each = local.vpcs

  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_route_table.public[each.key].id
}

# 5. VPC peering connections (full mesh)
resource "aws_vpc_peering_connection" "this" {
  for_each = local.peerings

  vpc_id      = aws_vpc.this[each.value.a].id
  peer_vpc_id = aws_vpc.this[each.value.b].id
  auto_accept = true

  tags = {
    Name = "${local.name_prefix}-pcx-${each.key}"
  }
}

# 6. Peering routes in both directions
resource "aws_route" "peer" {
  for_each = local.peer_routes

  route_table_id            = aws_route_table.public[each.value.route_table].id
  destination_cidr_block    = each.value.destination
  vpc_peering_connection_id = aws_vpc_peering_connection.this[each.value.peering].id
}
