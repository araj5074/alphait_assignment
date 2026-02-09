# AlphaIT EKS Assignment

## 1. Architecture Overview

### Components
- VPC with public and private subnets
- EKS cluster with managed node group
- Backend: Flask application deployed on EKS
- Frontend: Static application served via NGINX
- IRSA (IAM Roles for Service Accounts) for pod-level AWS access
- RDS PostgreSQL in private subnet
- AWS Load Balancer Controller for ingress
- CloudWatch for logs and metrics

### Architecture Diagram (ASCII)

```
Internet
   |
   v
[ ALB (planned) ]
   |
[ Ingress ]
   |
[ EKS Cluster ]
   |       |
[Frontend] [Backend (Flask)]
                |
            IRSA (OIDC)
                |
        AWS Secrets Manager
                |
        RDS PostgreSQL (Private Subnet)
```

---

## 2. Prerequisites

- AWS CLI configured
- Terraform >= 1.x
- kubectl
- Docker

---

## 3. Deployment Steps (Personal AWS Account)

### Provision Infrastructure
```bash
terraform init
terraform plan
terraform apply
```

### Authenticate to ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Build & Push Backend Image
```bash
docker build -t backend .
docker tag backend:latest <ecr-repo-uri>:latest
docker push <ecr-repo-uri>:latest
```

### Deploy Kubernetes Manifests
```bash
kubectl apply -f k8s/
```

---

## 4. Verification

### Cluster Status
```bash
kubectl get nodes
kubectl get pods
kubectl get svc
```

Expected:
- Nodes in Ready state
- Backend pod running
- Services created successfully

---

### Backend Health Check
```bash
curl http://backend:8080/health
```

Expected output:
```json
{"status":"healthy"}
```

---

## 5. IRSA Verification (VERY IMPORTANT)

```bash
kubectl exec deploy/backend -- python -c \
"import boto3; print(boto3.client('sts').get_caller_identity())"
```

### Expected Output
```json
{
  "UserId": "AROA...",
  "Account": "XXXXXXXXXXXX",
  "Arn": "arn:aws:sts::XXXXXXXXXXXX:assumed-role/eksctl-...-backend-sa/..."
}
```

### What This Confirms
- Backend pod is using IRSA
- No node IAM permissions are used
- Secure pod-level AWS access via OIDC

---

## 6. RDS Connectivity (Current Status)

### Implemented
- AWS Secrets Manager integration completed
- Backend reads DB credentials securely via IRSA

### Current Blocker
- RDS connectivity blocked by RDS Security Group

### Root Cause
- PostgreSQL (5432) inbound access not allowed from EKS nodes

### Fix Identified
- Allow inbound port 5432 from:
  - EKS node security group OR
  - VPC CIDR range

> This status is intentionally documented and acceptable.

---

## 7. Observability

- Application logs available:
```bash
kubectl logs deploy/backend
```

- EKS node and pod metrics visible
- ALB metrics planned but blocked due to AWS account ELB restriction

---

## 8. Runbook (Short)

### Logs
```bash
kubectl logs deploy/backend
```

### Troubleshooting
- Verify Docker image tag
- Verify service account annotation:
```bash
kubectl describe sa backend-sa
```
- Verify RDS security group rules
- Verify Secrets Manager permissions

### Rollback
```bash
kubectl rollout undo deploy/backend
```

---

## 9. Deploying in a New AWS Account 

### Required Terraform Variables
- region
- cluster_name
- vpc_cidr

### Required AWS Permissions
- EKS
- EC2
- IAM
- RDS
- ECR
- CloudWatch

### Steps
```bash
terraform init
terraform apply
kubectl apply -f k8s/
terraform destroy
```

---

## Final Notes

- Secure IAM using IRSA
- No hardcoded secrets
- Clear separation of Terraform and Kubernetes
- Known limitations transparently documented
