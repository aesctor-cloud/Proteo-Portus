resource "aws_sfn_state_machine" "Raw_to_Gold_pipeline" {
  name     = "Raw_to_Gold_pipeline"
  role_arn = var.arn_step_functions

  definition = <<EOF
    {
  "Comment": "Raw to Gold pipeline",
  "StartAt": "Extract and analyze",
  "States": {
    "Extract and analyze": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:extract_and_analyze:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.error_detail",
          "Next": "Loguear error Extract"
        }
      ],
      "Next": "Validación"
    },
    "Loguear error Extract": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:error_logger:$LATEST"
      },
      "End": true
    },
    "Validación": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:validation:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Mapear registros"
    },
    "Mapear registros": {
      "Type": "Map",
      "ItemsPath": "$.results",
      "ResultPath": "$",
      "Iterator": {
        "StartAt": "¿Es válido?",
        "States": {
          "¿Es válido?": {
            "Type": "Choice",
            "Choices": [
              {
                "Variable": "$.valid",
                "BooleanEquals": true,
                "Next": "Transformar válido"
              },
              {
                "Variable": "$.valid",
                "BooleanEquals": false,
                "Next": "Loguear inválido"
              }
            ],
            "Default": "Omitir inválido"
          },
          "Transformar válido": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:eu-west-1:084375571972:function:transformation:$LATEST",
            "ResultPath": "$.valid_result",
            "End": true
          },
          "Loguear inválido": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
              "Payload.$": "$",
              "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:error_logger:$LATEST"
            },
            "Retry": [
              {
                "ErrorEquals": [
                  "Lambda.ServiceException",
                  "Lambda.AWSLambdaException",
                  "Lambda.SdkClientException",
                  "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds": 1,
                "MaxAttempts": 3,
                "BackoffRate": 2,
                "JitterStrategy": "FULL"
              }
            ],
            "End": true
          },
          "Omitir inválido": {
            "Type": "Pass",
            "Result": "Sin campo 'valid', omitiendo registro",
            "End": true
          }
        }
      },
      "Next": "Load in Silver"
    },
    "Load in Silver": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:load:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Silver to Gold"
    },
    "Silver to Gold": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:silver_to_gold:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.error_detail",
          "Next": "Loguear error Gold"
        }
      ],
      "End": true
    },
    "Loguear error Gold": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:error_logger:$LATEST"
      },
      "End": true
    }
  }
}
  EOF
}


resource "aws_sfn_state_machine" "Search_and_Evaluate_pipeline" {
  name     = "Search_and_Evaluate_pipeline"
  role_arn = var.arn_step_functions

  definition = <<EOF
    {
  "Comment": "Search_and_Evaluate_pipeline",
  "StartAt": "Extract",
  "States": {
    "Extract": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:extract_inference:$LATEST",
        "Payload.$": "$"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "LoggerError"
        }
      ],
      "ResultPath": "$.extract",
      "Next": "CheckHasResults"
    },
    "CheckHasResults": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.extract",
          "IsPresent": true,
          "Next": "SearchResults"
        }
      ],
      "Default": "LoggerError"
    },
    "LoggerError": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:error_logger:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "FailState"
    },
    "SearchResults": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:query_function:$LATEST",
        "Payload.$": "$"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "LoggerError"
        }
      ],
      "ResultPath": "$.search",
      "Next": "EvaluateOutput"
    },
    "EvaluateOutput": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:eu-west-1:084375571972:function:output_evaluator:$LATEST",
        "Payload.$": "$"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "LoggerError"
        }
      ],
      "ResultPath": "$.evaluation",
      "End": true
    },
    "FailState": {
      "Type": "Fail",
      "Error": "PipelineFailed",
      "Cause": "A task failed after retries or no results found"
    }
  }
}
  EOF
}
