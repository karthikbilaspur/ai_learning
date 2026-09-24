variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "key_name" {
  type        = string
  default     = null
  description = "Name of an existing EC2 key pair to attach, so you can SSH in. Create one in the AWS console (EC2 > Key Pairs) first, then set this to its name."
}
