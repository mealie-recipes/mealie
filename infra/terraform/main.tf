data "openstack_images_image_v2" "image" {
  name = var.instance_image_name
}

data "openstack_networking_network_v2" "network" {
  name = var.network_name
}

resource "openstack_networking_secgroup_v2" "mealie" {
  name        = var.security_group_name
  description = "Security group for the Mealie stack"
}

resource "openstack_networking_secgroup_rule_v2" "ingress_tcp" {
  for_each          = toset([for p in var.allowed_tcp_ports : tostring(p)])
  security_group_id = openstack_networking_secgroup_v2.mealie.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = tonumber(each.value)
  port_range_max    = tonumber(each.value)
}

resource "openstack_compute_instance_v2" "mealie" {
  name        = var.instance_name
  image_id    = data.openstack_images_image_v2.image.id
  flavor_name = var.instance_flavor_name
  key_pair    = var.keypair_name

  security_groups = [openstack_networking_secgroup_v2.mealie.name]

  network {
    uuid = data.openstack_networking_network_v2.network.id
  }
}

resource "openstack_networking_floatingip_v2" "mealie" {
  pool = var.floating_ip_pool
}

resource "openstack_compute_floatingip_associate_v2" "mealie" {
  floating_ip = openstack_networking_floatingip_v2.mealie.address
  instance_id  = openstack_compute_instance_v2.mealie.id
}
