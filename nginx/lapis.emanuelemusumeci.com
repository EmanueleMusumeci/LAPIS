server {
    server_name lapis.emanuelemusumeci.com;

    root /var/www/lapis.emanuelemusumeci.com;
    index index.html;

    # Security headers (matching existing sites)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # WebSocket proxy (real-time pipeline updates)
    location /ws/ {
        proxy_pass         http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600s;
    }

    # API proxy
    location /api/ {
        proxy_pass         http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        client_max_body_size 2m;
    }

    # Static plan results
    location /static/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # SPA frontend — serve static files, fall back to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|svg|woff2|ico)$ {
        try_files $uri =404;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    listen 443 ssl;
    listen [::]:443 ssl;
    ssl_certificate /etc/letsencrypt/live/lapis.emanuelemusumeci.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lapis.emanuelemusumeci.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    listen [::]:80;
    server_name lapis.emanuelemusumeci.com;

    if ($host = lapis.emanuelemusumeci.com) {
        return 301 https://$host$request_uri;
    }

    return 404;
}
