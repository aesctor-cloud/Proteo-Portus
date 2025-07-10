resource "aws_s3_bucket" "bucket-proteo-energia" {
  bucket = "raw-bucket-proteo-energia"
  
  tags = {
    Name        = "raw-bucket-proteo-energia"
    Environment = "Test"
  }
}
