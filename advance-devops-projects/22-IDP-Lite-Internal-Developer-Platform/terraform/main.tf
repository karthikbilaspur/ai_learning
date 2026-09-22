module "env" {
  source = "./modules/env"
  team = var.team
  db_url = var.db_url
}
variable "team" {}
variable "db_url" {}
