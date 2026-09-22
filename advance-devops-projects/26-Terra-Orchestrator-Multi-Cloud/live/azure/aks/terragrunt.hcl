include { path = find_in_parent_folders() }
terraform { source = "../../../modules/aks-app" }
inputs = { cluster_name = "prod-azure", location = "eastus" }
