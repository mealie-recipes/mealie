# Terraform Layout

This directory is the infrastructure layer for the Chameleon deployment.

Recommended responsibilities:

- create the VM or instance
- create security groups and firewall rules
- allocate and attach a floating IP
- optionally create persistent storage

This repo keeps the application and monitoring manifests in Kubernetes YAML.
Terraform should stay focused on provisioning the machine that runs those workloads.

Typical workflow:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

Use the `terraform.tfvars.example` file as a starting point for environment-specific values.
