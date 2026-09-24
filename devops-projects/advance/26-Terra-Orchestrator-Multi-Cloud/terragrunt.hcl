remote_state {
  backend = "s3"
  generate = {path = "backend.tf", if_exists = "overwrite"}
  config = { bucket = "tf-state-orchestrator-2026", key = "${path_relative_to_include()}/terraform.tfstate", region = "us-east-1", encrypt = true, dynamodb_table = "tf-lock" }
}
generate "provider" { path = "provider.tf" if_exists = "overwrite_terragrunt" contents = "provider aws { region = \"us-east-1\" }" }
