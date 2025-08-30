# AWS Sales Data Pipeline

A dummy data engineering project demonstrating AWS services with CI/CD.

## Architecture
- Data Source: CSV files in S3
- Processing: AWS Lambda (Python)
- Orchestration: AWS Step Functions
- Catalog: AWS Glue Data Catalog
- Query: Amazon Athena
- Infrastructure as Code: AWS CDK
- CI/CD: GitHub Actions

## Setup
1. Clone the repository
2. Set up Python virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Deploy: `cdk deploy`

## Project Structure