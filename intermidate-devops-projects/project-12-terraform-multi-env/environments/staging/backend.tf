terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state: every environment gets its own state file (via "key"),
  # in the same S3 bucket, locked with the same DynamoDB table so two
  # people (or two CI runs) can never apply at the same time.
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "devops-starter/staging/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
