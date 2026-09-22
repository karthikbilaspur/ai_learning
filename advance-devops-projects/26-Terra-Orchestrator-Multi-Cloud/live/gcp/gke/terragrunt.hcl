include { path = find_in_parent_folders() }
terraform { source = "../../../modules/gke-app" }
inputs = { cluster_name = "prod-gcp", zone = "us-central1-a" }
