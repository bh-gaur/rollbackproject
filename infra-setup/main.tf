provider "aws" {
  region = "us-east-1"
}

# Create a small, cheap VPC for your cluster
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name                 = "project-vpc"
  cidr                 = "10.0.0.0/16"
  azs                  = ["us-east-1a", "us-east-1b"]
  public_subnets       = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets      = ["10.0.10.0/24", "10.0.11.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true # Saves money on NAT Gateways
}

# Provision the EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "devops-college-project"
  cluster_version = "1.31"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Grant your current AWS IAM identity access to the cluster automatically
  enable_cluster_creator_admin_permissions = true

  # Set up cheap node groups using standard EC2 Free Tier types
  eks_managed_node_groups = {
    workers = {
      min_size       = 1
      max_size       = 2
      desired_size   = 2
      instance_types = ["t3.micro"] # Low cost
    }
  }
}
