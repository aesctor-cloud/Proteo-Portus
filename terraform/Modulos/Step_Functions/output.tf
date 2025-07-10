output "target_arn_step_functions" {
  description = "arn targget for event bridge"
  value= aws_sfn_state_machine.Raw_to_Gold_pipeline.arn
}