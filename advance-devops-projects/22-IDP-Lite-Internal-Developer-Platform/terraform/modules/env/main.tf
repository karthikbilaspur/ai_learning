resource "kubernetes_namespace" "team" { metadata { name = var.team } }
resource "kubernetes_secret" "app" {
  metadata { name = "app-secret" namespace = var.team }
  data = { DB_URL = var.db_url }
}
variable "team" {}
variable "db_url" {}
