template {
  source = "/etc/consul-templates/load-balancer.tpl"
  destination = "/etc/nginx/sites-available/load-balancer"
  command = "ln -sf /etc/nginx/sites-available/load-balancer /etc/nginx/sites-enabled/load-balancer && systemctl reload nginx"
}
