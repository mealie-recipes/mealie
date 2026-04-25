# Infrastructure Workflow

This directory separates the deployment workflow into two layers and keeps it independent from the notebook:

- `terraform/` provisions infrastructure
- `ansible/` configures the VM and deploys the stack

The notebook can still exist as an orchestration helper, but it is no longer the primary deployment path.

Suggested responsibilities:

## Terraform

- security groups
- instance provisioning
- networking
- floating IPs
- any long-lived infrastructure resources

## Ansible

- install host packages
- clone the repo
- prepare the runtime environment
- run the deployment script
- restart and verify services

## Notebook

Use the notebook only if you want a higher-level orchestration layer.
The Terraform and Ansible paths in this directory should work on their own.

It can still:

- create the lease
- choose the project/site
- launch the VM
- call Terraform or Ansible after bootstrapping

Typical standalone flow:

```text
terraform apply -> ansible-playbook -> kubectl apply via scripts/deploy.sh
```
