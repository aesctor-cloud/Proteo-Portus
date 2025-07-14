resource "aws_s3_bucket" "bucket-proteo-energia" {
  bucket = "raw-bucket-proteo"
  
  tags = {
    Name        = "raw-bucket-proteo"
    Environment = "Test"
  }
}

