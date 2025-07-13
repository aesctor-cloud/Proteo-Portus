#---------------------------------------------------------------Lambda extract function------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "extract_function" {
  function_name = "extract_and_analyze"
  timeout       = 200 # seconds
  image_uri = var.image_uri_extract
  package_type  = "Image"
  memory_size   = 1024

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "extract_and_analyze function"
  }

}

#---------------------------------------------------------------Lambda validation function------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "validation_function" {
  function_name = "validation"
  timeout       = 200 # seconds
  image_uri = var.image_uri_validation
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "validation function"
  }
}

#---------------------------------------------------------------Lambda transformation function ------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "transformation_function" {
  function_name = "transformation"
  timeout       = 200 # seconds
  image_uri = var.image_uri_transformation
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }
  tags={
    Name = "tansform function"
  }

}

# #---------------------------------------------------------------Lambda load function ------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "load_function" {
  function_name = "load"
  timeout       = 200 # seconds
  image_uri = var.image_uri_load
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "load function"
  }

}

#---------------------------------------------------------------Lambda log function ------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "log_function" {
  function_name = "error_logger"
  timeout       = 200 # seconds
  image_uri = var.image_uri_log
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }
  tags={
    Name = "log function"
  }


}

#---------------------------------------------------------------Lambda init pgvector function ------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "init_pgvector" {
  function_name = "init_pgvector"
  timeout       = 200 # seconds
  image_uri = var.image_uri_pgvector
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "init pgvector function"
  }
}

#---------------------------------------------------------------Lambda embeddings function ------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "silver2gold" {
  function_name = "silver_to_gold"
  timeout       = 200 # seconds
  image_uri = var.image_uri_silver2gold
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "silver to gold function"
  }
}

#--------------------------------------------------------------- Extract inference function ------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "extract_inference" {
  function_name = "extract_inference"
  timeout       = 200 # seconds
  image_uri = var.image_uri_inference
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }
  tags={
    Name = "inference function"
  }


}

#--------------------------------------------------------------- Query function ------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "Query_function" {
  function_name = "query_function"
  timeout       = 200 # seconds
  image_uri = var.image_uri_query
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }

  environment {
    variables = {
      RDS_HOST     = var.hostname_rds
      RDS_PORT     = var.port_rds
      RDS_USER     = var.username_rds
      RDS_PASSWORD = var.password_rds
      RDS_DB       = var.database_name
    }
  }
  tags={
    Name = "query function for best result"
  }
}

#--------------------------------------------------------------- output function ------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "output_function" {
  function_name = "output_evaluator"
  timeout       = 200 # seconds
  image_uri = var.image_uri_output
  package_type  = "Image"
  memory_size   = 512

  role = var.arn_role_lambda
  vpc_config {
    subnet_ids         = [var.subnet_a_id, var.subnet_b_id]
    security_group_ids = [var.security_group_lambda]
  }
  tags={
    Name = "output evaluator function"
  }


}