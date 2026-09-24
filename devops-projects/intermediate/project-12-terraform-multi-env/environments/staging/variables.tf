variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "instance_type" {
  type = string
}

variable "key_name" {
  type    = string
  default = null
}

variable "ssh_cidr_blocks" {
  type = list(string)
}
