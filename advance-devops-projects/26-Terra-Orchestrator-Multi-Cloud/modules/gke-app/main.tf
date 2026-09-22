resource "google_container_cluster" "gke" { name = var.cluster_name location = var.zone initial_node_count = 2 }
variable "cluster_name" {}
variable "zone" {}
