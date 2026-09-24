module "network" {
  source = "../../modules/network"

  env_name        = "prod"
  ssh_cidr_blocks = var.ssh_cidr_blocks
}

module "compute" {
  source = "../../modules/compute"

  env_name           = "prod"
  instance_type      = var.instance_type
  key_name           = var.key_name
  security_group_id  = module.network.security_group_id
}

output "public_ip" {
  value = module.compute.public_ip
}

output "ssh_command" {
  value = module.compute.ssh_command
}
