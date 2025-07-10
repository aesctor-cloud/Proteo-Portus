terraform {
  backend "s3" {
    bucket         = "proteo-portus-terraform-state"
    key            = "env/test/terraform.tfstate"
    region         = "eu-west-1"

}
}