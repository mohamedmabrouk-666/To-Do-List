resource "aws_instance" "jenkins_ec2" {

  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name = "Terraform-Jenkins-EC2"
  }
}
