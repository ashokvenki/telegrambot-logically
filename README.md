# CloudBots – Telegram Bot Infrastructure on AWS (Terraform)

## Project Overview

This project implements the backend infrastructure for a Telegram bot using **AWS** and **Terraform**.  
The primary goal is not only to deploy a working bot, but to demonstrate **Infrastructure as Code best practices**, including:

- Modular Terraform design
- Remote Terraform state
- Environment separation
- IAM least-privilege design
- Adaptation to AWS Academy constraints
- Safe refactoring without data loss

The project was developed incrementally and refactored based on a formal **gap analysis**, simulating how infrastructure evolves in real-world environments.

---

## High-Level Architecture

The Telegram bot backend is built using a serverless architecture:

### Components

- **AWS Lambda** – Handles Telegram webhook requests
- **Amazon API Gateway** – Public HTTPS webhook endpoint
- **Amazon DynamoDB** – Persistent user data storage
- **Amazon S3** – User-uploaded file storage
- **AWS IAM** – Execution permissions via AWS Academy LabRole
- **Terraform S3 Backend** – Remote state storage

---

## Why Serverless?

- No server management
- Scales automatically
- Cost-efficient
- Native webhook integration

---

## Terraform Design Philosophy

- Separation of concerns  
- Reusability  
- Minimal blast radius  
- Safe state migration  

---

## Modular Terraform Structure

```
modules/
├── api_gateway/
├── lambda/
├── dynamodb/
├── s3/
└── iam/
```

---

## Environment Separation

Environment-specific configuration via variables:
```hcl
environment = "dev"
```

---

## Remote Terraform State

- Bucket: cloudbots-terraform-state
- Key: telegram-bot/terraform.tfstate

DynamoDB locking is omitted due to AWS Academy restrictions.

---

## IAM and AWS Academy Constraints

- Least-privilege policies designed for Lambda
- IAM role creation restricted in AWS Academy
- Pre-existing LabRole is used

---

## Tagging Strategy

- Project = telegram-bot
- Environment = dev
- Owner = CloudBots

---

## Deployment

```bash
terraform init -reconfigure
terraform apply
```

### Destroy
```bash
terraform destroy
```

---

## Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" -d "url=$(terraform output -raw api_gateway_webhook_url)"
```

---

## Summary

This project demonstrates modular Terraform, remote state, IAM best practices, and safe refactoring under AWS Academy constraints.
