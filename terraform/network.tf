# ------------------------------------------------------------------------------
# DevOrbit network layer
# Owner: Member 1 (Cloud/Infra) - VPC-A
#
#   VPC-A infra 10.10.0.0/16  -> bastion / management
#   VPC-B app   10.20.0.0/16  -> k3s cluster and DevOrbit application (Member 2)
#   VPC-C ci    10.30.0.0/16  -> Jenkins CI/CD host (Member 3)
#
# VPC peering is non-transitive, so all three peering links are created.
# Member 2 and Member 3 only add resources inside their own VPC; this file
# keeps the shared network and peering stable so their work composes cleanly.
# ------------------------------------------------------------------------------

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
