include { path = find_in_parent_folders() }
terraform { source = "../../../modules/eks-app" }
inputs = { cluster_name = "prod-aws", instance_type = "t3.medium" }
