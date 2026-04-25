variable "openstack_auth_url" {
  description = "OpenStack auth endpoint for the Chameleon environment."
  type        = string
}

variable "openstack_tenant_name" {
  description = "OpenStack project or tenant name."
  type        = string
}

variable "openstack_username" {
  description = "OpenStack username."
  type        = string
}

variable "openstack_password" {
  description = "OpenStack password."
  type        = string
  sensitive   = true
}

variable "openstack_region" {
  description = "OpenStack region."
  type        = string
  default     = "KVM@TACC"
}

variable "instance_name" {
  description = "Name of the Mealie VM."
  type        = string
  default     = "mealie-node"
}

variable "instance_image_name" {
  description = "Image name to boot."
  type        = string
  default     = "Ubuntu 22.04"
}

variable "instance_flavor_name" {
  description = "Flavor name for the instance."
  type        = string
}

variable "keypair_name" {
  description = "SSH keypair name registered in OpenStack."
  type        = string
}

variable "network_name" {
  description = "Private network to attach the instance to."
  type        = string
  default     = "sharednet1"
}

variable "security_group_name" {
  description = "Security group name for the instance."
  type        = string
  default     = "mealie-sg"
}

variable "floating_ip_pool" {
  description = "Floating IP pool name used by OpenStack/Chameleon."
  type        = string
}

variable "allowed_tcp_ports" {
  description = "TCP ports to open for the service."
  type        = list(number)
  default     = [22, 30090, 30091, 30300, 30903, 30500, 30800, 30900, 30901]
}
