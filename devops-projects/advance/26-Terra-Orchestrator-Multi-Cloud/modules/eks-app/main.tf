module "eks" { source = "terraform-aws-modules/eks/aws" version = "~> 20.0" cluster_name = var.cluster_name }
variable "cluster_name" {}
variable "instance_type" { default = "t3.medium" }
resource "helm_release" "app" { name = "myapp" chart = "../../charts/myapp" namespace = "prod" }
