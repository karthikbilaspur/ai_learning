# Project 12 — Multi-Environment Terraform with Modules & Remote State

Project 8 (beginner series) had one flat `main.tf` for one server. Real
teams need dev/staging/prod that don't share state, plus reusable code
instead of copy-pasted `.tf` files. This project restructures that into
modules + per-environment remote state.

## What's here
- `modules/network/` — reusable security group module (SSH CIDR is a
  variable, so prod can lock it down while dev stays open)
- `modules/compute/` — reusable EC2 instance module (same `user_data`
  Docker install as Project 8)
- `environments/dev/`, `environments/staging/`, `environments/prod/` —
  each wires the two modules together with its own variables and its own
  remote state file

## Assumes
An AWS account, an S3 bucket for state, and a DynamoDB table for locking
(create these once, by hand or with a tiny separate Terraform config —
they can't manage the state they themselves live in).

## What to do

1. Create the state bucket and lock table once (outside this project):
   ```bash
   aws s3api create-bucket --bucket your-terraform-state-bucket --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1
   aws dynamodb create-table --table-name terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```
2. Update `bucket` in every `environments/*/backend.tf` to your bucket name.
3. Work in one environment at a time, e.g. dev:
   ```bash
   cd environments/dev
   cp terraform.tfvars.example terraform.tfvars
   terraform init
   terraform plan -var="key_name=your-key-pair-name"
   terraform apply -var="key_name=your-key-pair-name"
   ```
4. Now do the same in `environments/staging/` — notice it's the exact same
   module code, just different variables, and its state is a completely
   separate file (`devops-starter/staging/terraform.tfstate`) so applying
   staging can never touch dev's resources.
5. Compare `prod/terraform.tfvars.example` to `dev`'s — prod restricts SSH
   to a single IP instead of the world.
6. Destroy each environment when you're done:
   ```bash
   terraform destroy -var="key_name=your-key-pair-name"
   ```

## Concepts to know before moving on
- Why state is split *per environment*, not per resource
- What DynamoDB locking actually prevents (two `apply`s racing each other)
- Modules as "functions" for infrastructure — same code, different inputs
- Why prod's variables differ from dev's, not just its resource sizes

Next: **Project 13 — Packaging the App as a Helm Chart**
