terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
}

module "iam" {
  source       = "./modules/iam"
  project_name = var.project_name
}

module "eks" {
  source        = "./modules/eks"
  project_name  = var.project_name
  cluster_name  = "${var.project_name}-eks"
  subnet_ids    = module.vpc.private_subnet_ids
  eks_role_arn  = module.iam.eks_cluster_role_arn
  node_role_arn = module.iam.eks_node_role_arn
}

module "rds" {
  source       = "./modules/rds"
  project_name = var.project_name
  db_name      = var.db_name
  db_user      = var.db_user
  db_password  = var.db_password
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
  vpc_sg_id    = module.vpc.default_sg_id
}

module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  bucket_name  = var.s3_bucket_name
}

module "alb" {
  source       = "./modules/alb"
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}
