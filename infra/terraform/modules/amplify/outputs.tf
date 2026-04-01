output "amplify_app_id" {
  value = aws_amplify_app.frontend.id
}

output "amplify_app_url" {
  value = "https://${aws_amplify_branch.main.branch_name}.${aws_amplify_app.frontend.default_domain}"
}

output "amplify_app_domain" {
  value = aws_amplify_app.frontend.default_domain
}
