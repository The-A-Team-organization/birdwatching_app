upstream backend {
  {{ range service "web" }}
      server {{ .Address }}:{{ .Port }};
  {{ end }}
}

server {
    listen {{ key "nginx/lb_port" }};
    server_name _;
    location / {
        proxy_pass http://backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

