module "bucket" {
  source = "./Modulos/bucket"
}

module "lambdas_functions" {
  source          = "./Modulos/lambdas_functions"
  # bucket_arn     = module.bucket.arn
  # bucket_name = module.bucket.bucket_name
  arn_role_lambda = var.arn_role_lambda
  subnet_a_id = module.vpc_sg.subnet_a_id
  subnet_b_id = module.vpc_sg.subnet_b_id
  security_group_lambda = module.vpc_sg.security_group_lambda
  password_rds = module.rds.db_password
  port_rds = module.rds.db_port
  hostname_rds = module.rds.db_host
  username_rds = module.rds.db_user
  database_name = module.rds.db_name
  image_uri_extract = module.docker_push_extract.image_uri
  image_uri_validation = module.docker_push_validation.image_uri
  image_uri_transformation = module.docker_push_transformation.image_uri
  image_uri_load = module.docker_push_load.image_uri
  image_uri_log = module.docker_push_log.image_uri
  image_uri_pgvector = module.docker_push_pgvector.image_uri
  image_uri_silver2gold = module.docker_push_silver2gold.image_uri
 }

module "docker_push_extract"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_extract
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "extract"
}

module "docker_push_validation"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_validation
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "validation"
}

module "docker_push_transformation"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_transformation
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "transformation"
}

module "docker_push_load"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_load
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "load"
}

module "docker_push_log"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_log
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "log"
}

module "docker_push_pgvector"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_pgvector
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "pgvector"
}

module "docker_push_silver2gold"{
  source = "./Modulos/Docker_push"
  repository_name = var.repo_portus
  path_to_dockerfile = var.path_to_dockerfile_silver2gold
  repository_url = module.create_repo.repository_url
  depends_on = [ module.create_repo ]
  image_tag = "silver_to_gold"
}

module "create_repo" {
  source = "./Modulos/ECR"
  repository_name = var.repo_portus
}

module "vpc_sg" {
  source = "./Modulos/VPC+SG"
}

module "rds" {
  source = "./Modulos/RDS"
  private_subnets_rds = module.vpc_sg.private_subnets_rds
  security_groups_rds = module.vpc_sg.security_groups_rds
  db_password = var.db_password
}

module "init_pgvector" {
  source = "./Modulos/PGVECTOR"
  lambda_pgvector = module.lambdas_functions.lambda_pgvector_name
  depends_on = [module.rds, module.lambdas_functions]
  
}

module "Step_Functions" {
  source = "./Modulos/Step_Functions"
  arn_step_functions = var.arn_step_functions
  depends_on = [ module.lambdas_functions ]
}

module "EventBridge"{
  source= "./Modulos/Event_bridge"
  arn_bucket=module.bucket.arn
  target_arn_step_functions = module.Step_Functions.target_arn_step_functions
  lambda_function_name = "extract_and_analyze"
  event_bridge_arn = var.event_bridge_arn
  depends_on = [ module.Step_Functions ]

}