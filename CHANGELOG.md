# CHANGELOG

## Task 8.2 – Terraform Refactor

### Added
- Modular Terraform structure for Lambda, API Gateway, DynamoDB, S3, and IAM
- Remote Terraform state using an S3 backend
- Environment-based configuration (dev/prod via variables)
- Centralized tagging strategy (Project, Environment, Owner)

### Changed
- Refactored root Terraform configuration to wire modules via variables and outputs
- Migrated existing Terraform state using `terraform state mv` to avoid resource recreation
- Updated API Gateway configuration to support environment-based stages

### Removed
- Inline resource definitions from the root module
- IAM role creation (replaced with AWS Academy LabRole usage)
- Unused IAM policy enforcement due to AWS Academy restrictions

### Notes
- Least-privilege IAM policies were designed and documented but cannot be enforced programmatically in AWS Academy
- No stateful resources (DynamoDB or S3) were destroyed during the refactor
