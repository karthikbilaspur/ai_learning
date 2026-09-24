terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "devops" {
  name        = "devops-starter-sg"
  description = "Security group for DevOps starter"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH - restrict this in production"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.devops.id]

  # Installs Docker automatically on first boot, using the same steps as
  # scripts/setup-ubuntu.sh, so the instance is ready for
  # `docker compose up -d --build` as soon as it's reachable.
  user_data = <<-EOF
    #!/usr/bin/env bash
    set -euo pipefail
    apt-get update
    apt-get install -y git curl docker.io docker-compose-plugin
    systemctl enable --now docker
    usermod -aG docker ubuntu
  EOF

  tags = {
    Name = "devops-starter"
  }
}

output "public_ip" {
  value = aws_instance.app.public_ip
}

output "ssh_command" {
  value       = "ssh ubuntu@${aws_instance.app.public_ip}"
  description = "Run this once the instance has finished its startup script (usually 1-2 minutes after apply)."
}
