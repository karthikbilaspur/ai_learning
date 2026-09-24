# Project 8 — Infrastructure as Code with Terraform

Provisions a real AWS server with code instead of clicking around the AWS
console, so the setup is repeatable and reviewable.

## What's here
- `terraform/main.tf` — an EC2 instance + security group (ports 22, 80
  open); Docker gets installed automatically on first boot via `user_data`
- `terraform/variables.tf` — `aws_region`, `instance_type`, `key_name`
- Everything from Project 7

## What to do

1. Read `terraform/README.md` first — it covers prerequisites (an AWS
   account and an existing EC2 key pair).
2. Initialize and preview:
   ```bash
   cd terraform
   terraform init
   terraform plan -var="key_name=your-key-pair-name"
   ```
3. Apply it, wait a minute or two, then SSH in using the `ssh_command`
   Terraform prints:
   ```bash
   terraform apply -var="key_name=your-key-pair-name"
   ```
4. On the server, clone your repo and run
   `docker compose up -d --build` — this is the manual version of what
   Project 7's deploy workflow describes.
5. **Destroy it when you're done** so you don't get charged:
   ```bash
   terraform destroy -var="key_name=your-key-pair-name"
   ```

## Concepts to know before moving on
- What "Infrastructure as Code" means and why it beats clicking in a
  console
- The `plan` → `apply` → `destroy` lifecycle
- Why `.tfstate` files and AWS credentials are never committed to Git

Next: **Project 9 — Container Orchestration with Kubernetes**
