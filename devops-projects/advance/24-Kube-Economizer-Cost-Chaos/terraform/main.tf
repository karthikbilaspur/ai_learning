variable "cluster_name" {}
module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"
  cluster_name = var.cluster_name
}
resource "helm_release" "kubecost" {
  name = "kubecost"
  repository = "https://kubecost.github.io/cost-analyzer/"
  chart = "cost-analyzer"
  namespace = "kubecost"
  create_namespace = true
  set { name = "kubecostToken" value = "demo" }
}
resource "helm_release" "chaos-mesh" {
  name = "chaos-mesh"
  repository = "https://charts.chaos-mesh.org"
  chart = "chaos-mesh"
  namespace = "chaos-mesh"
  create_namespace = true
}
