# Terraform

This folder provisions a basic AWS EC2 instance and security group.

## Prerequisites

- AWS account
- AWS CLI configured locally
- Terraform installed
- An existing EC2 key pair (EC2 console > Key Pairs > Create key pair), so you can SSH in

Docker is installed automatically when the instance first boots (see `user_data`
in `main.tf`), so there's no manual setup step once it's running — just wait a
minute or two after `apply` before SSHing in.

## Commands

Pass your key pair name when you plan:

```bash
terraform plan -var="key_name=your-key-pair-name"
terraform apply -var="key_name=your-key-pair-name"
```

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

When finished:

```bash
terraform destroy
```

## Important

This is a learning project. The SSH rule currently allows `0.0.0.0/0`.
For a real deployment, restrict SSH to your own IP or use a safer access method.

Do not commit AWS access keys, `.tfstate` files, or other secrets.
