resource "aws_amplify_app" "frontend" {
  name       = "${var.project_name}-gui"
  repository = var.github_repository

  # GitHub Personal Access Token (PAT)
  access_token = var.github_access_token

  build_spec = <<-EOT
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
            - env | grep -e APP_AWS -e S3_ -e DYNAMODB_ -e NEXT_ -e STEP_FUNCTION >> .env.production
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
          - .next/cache/**/*
  EOT

  # Environment Variables (Connecting to Backend)
  environment_variables = {
    APP_AWS_REGION             = var.aws_region
    S3_BUCKET_NAME             = var.s3_bucket_name
    DYNAMODB_TABLE_JOBS        = var.dynamodb_table_jobs
    DYNAMODB_TABLE_FORMATS     = var.dynamodb_table_formats
    STEP_FUNCTION_ARN          = var.step_function_arn
    
    # Secure backend access keys
    APP_AWS_ACCESS_KEY_ID      = var.frontend_access_key_id
    APP_AWS_SECRET_ACCESS_KEY  = var.frontend_secret_access_key
    
    # Public Settings
    NEXT_PUBLIC_API_URL        = "/api"
    
    # Environment Hints
    _NODE_VERSION_HINT         = "20"
    AMPLIFY_MONOREPO_APP_ROOT  = "frontend"
  }

  platform = "WEB_COMPUTE" # Required for Next.js SSR/App Router

  tags = {
    Name = "${var.project_name}-amplify-app"
  }
}

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = var.branch_name

  framework = "Next.js - SSR"
  stage     = "PRODUCTION"

  tags = {
    Name = "${var.project_name}-amplify-main-branch"
  }
}
