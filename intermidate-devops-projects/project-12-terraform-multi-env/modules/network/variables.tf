variable "env_name" {
  type        = string
  description = "Environment name, e.g. dev, staging, prod"
}

variable "ssh_cidr_blocks" {
  type        = list(string)
  default     = ["0.0.0.0/0"]
  description = "CIDR blocks allowed to SSH in. Restrict this per environment - prod should NOT be 0.0.0.0/0."
}
