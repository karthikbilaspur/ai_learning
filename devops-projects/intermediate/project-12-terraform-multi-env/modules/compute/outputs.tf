output "public_ip" {
  value = aws_instance.app.public_ip
}

output "ssh_command" {
  value = "ssh ubuntu@${aws_instance.app.public_ip}"
}
