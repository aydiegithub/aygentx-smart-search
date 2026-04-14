# AygentX Deployment Guide

This guide describes how to configure the repository to deploy AygentX seamlessly as an AWS Lambda function using AWS SAM via GitHub Actions.

## Requirements Checklist
1. AWS account access (IAM user or OIDC Provider).
2. Access to GitHub Repository Secrets.

## Configuration Steps

### 1. Set Up the IAM User in AWS
GitHub Actions relies on AWS IAM credentials to use the `aws-actions/configure-aws-credentials` and execute the SAM commands.
* Go to the **AWS IAM Console**.
* Create a new **IAM User** specifically for CI/CD deployments (e.g., `github-actions-aygentx`).
* Ensure it has sufficient permissions (e.g. `AWSCloudFormationFullAccess`, `AWSLambda_FullAccess`, `AmazonAPIGatewayAdministrator`, `AmazonS3FullAccess`, `IAMFullAccess`). 
* Create an **Access key** and note the **Access Key ID** and **Secret Access Key**. *Warning: Treat these carefully!*

*(Alternately, configure an OpenID Connect (OIDC) identity provider for GitHub to avoid storing long-lived keys).*

### 2. Add Necessary Secrets in GitHub
Navigate to your repository on GitHub. Click **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.

You must create **all** of the following secrets exactly with these names for the GitHub Actions pipeline to run flawlessly:

#### AWS Credentials
| Secret Name | Description |
|---|---|
| `AWS_REGION` | Your preferred AWS region (e.g. `us-east-1` or `eu-west-1`). |
| `AWS_ACCESS_KEY_ID` | Your CI/CD IAM user API ID. |
| `AWS_SECRET_ACCESS_KEY` | Your CI/CD IAM user secret. |

#### AygentX Runtime Variables (Lambda Env)
| Secret Name | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API Key |
| `OPENAI_API_KEY` | OpenAI API Token |
| `API_SECRET_KEY` | Create a random string (e.g., `openssl rand -hex 64`) to secure your own API endpoints. |
| `CLOUDFLARE_DATABASE_ID` | The ID of your Cloudflare D1 database |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare Account ID |
| `CLOUDFLARE_API_TOKEN` | Bearer token allowing Cloudflare D1 querying |

---

## The Workflow Overview

With everything saved, every time a new change is pushed to the `main` branch, GitHub Actions will:
1. Initialize an Ubuntu runner and install `uv` + `python 3.12`.
2. Generate the dynamic `requirements.txt`.
3. Set up AWS SAM CLI and assume your AWS identity credentials.
4. Run `sam build` (or `sam build --use-container` for Lambda compatibility).
5. Run `sam deploy --resolve-s3` to automatically package the code, provision a managed hidden S3 bucket for artifacts, and deploy the AWS Lambda instance. The SAM process dynamically pushes your GitHub Secrets across to Lambda's environment variables.
