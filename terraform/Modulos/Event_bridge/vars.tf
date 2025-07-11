variable "bucket_name" {
    description = "Name of buycket raw"
    type        = string
  
}

variable "target_arn_step_functions" {    
    description = "arn lambda function"
    type        = string
  
}

variable "lambda_function_name"{
    description = "name lambda function"
    type        = string
}

variable "event_bridge_arn" {
    description = "arn event bridge"
    type = string
  
}
