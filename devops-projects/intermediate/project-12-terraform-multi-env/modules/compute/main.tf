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

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [var.security_group_id]

  user_data = <<-EOF2
    #!/usr/bin/env bash
    set -euo pipefail
    apt-get update
    apt-get install -y git curl docker.io docker-compose-plugin
    systemctl enable --now docker
    usermod -aG docker ubuntu
  EOF2

  tags = {
    Name        = "${var.env_name}-devops-starter"
    Environment = var.env_name
  }
}
