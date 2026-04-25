terraform {
  required_version = ">= 1.6.0"

  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.54"
    }
  }
}

provider "openstack" {
  auth_url    = var.openstack_auth_url
  tenant_name = var.openstack_tenant_name
  user_name   = var.openstack_username
  password    = var.openstack_password
  region      = var.openstack_region
}
