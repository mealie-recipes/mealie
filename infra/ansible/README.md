# Ansible Layout

This directory is the configuration and deployment layer for the Mealie stack, separate from the notebook.

Recommended responsibilities:

- install OS dependencies
- prepare the host for Kubernetes tooling
- clone or update the application repository
- deploy the stack and monitoring manifests
- verify services are healthy after deployment

Typical workflow:

```bash
cd infra/ansible
ansible-playbook playbooks/bootstrap.yml
ansible-playbook playbooks/deploy.yml
```

If you prefer a single entry point, `playbooks/site.yml` imports both playbooks.
