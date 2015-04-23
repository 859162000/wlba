upstream apps {
    server 10.160.45.30:8056;
    server 10.132.65.175:8056;
}

server {
    listen 80;
    server_name www.wanglibao.com wanglibao.com staging.wanglibao.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl spdy;
    server_name wanglibao.com;
    ssl_certificate /usr/local/nginx/ssl/wanglibao.crt;
    ssl_certificate_key /usr/local/nginx/ssl/wanglibao.key;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers RC4:HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    return 301 https://www.wanglibao.com$request_uri;
}
server {
    listen 443 ssl spdy;
    server_name www.wanglibao.com staging.wanglibao.com;
    ssl_certificate /usr/local/nginx/ssl/wanglibao.crt;
    ssl_certificate_key /usr/local/nginx/ssl/wanglibao.key;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers RC4:HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_prefer_server_ciphers on;

    charset utf-8;
    client_max_body_size 20m;
    client_body_timeout 600s;
    client_body_buffer_size 512k;
    client_header_buffer_size 512k;
    large_client_header_buffers 4 256k;

    access_log /tmp/access_wanglibao.log;
    error_log /tmp/error_wanglibao.log;
    
    location / {
        proxy_pass http://apps;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
        proxy_http_version 1.1;
    }

    location ~ ^/robots.txt{
        root /var/www/wanglibao/wanglibao-backend/static;
        access_log off;
    }

    location /currentstatus {
        stub_status on;
        access_log off;
    }

    location ~ /.git/ {
        deny all;
    }

    location ~ ^/static/m_js/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|htc|apk|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/wanglibao-backend/wanglibao_mobile;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/m_images/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|htc|apk|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/wanglibao-backend/wanglibao_mobile;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/m_stylesheets/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|htc|apk|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/wanglibao-backend/wanglibao_mobile;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/admin/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|pdf|doc|swf|zip|htc|xls|apk|properties|exe|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/virt-wanglibao/lib/python2.7/site-packages/django/contrib/admin/;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/rest_framework/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|pdf|doc|swf|zip|htc|xls|apk|properties|exe|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/virt-wanglibao/lib/python2.7/site-packages/rest_framework;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/ckeditor/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|pdf|doc|swf|zip|htc|xls|apk|properties|exe|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/virt-wanglibao/lib/python2.7/site-packages/ckeditor;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location ~ ^/static/.*\.(css|js|html|htm|jpg|jpeg|gif|png|ico|pdf|doc|swf|zip|htc|xls|apk|properties|exe|ttf|woff|map|svg|eot){
        root /var/www/wanglibao/wanglibao-backend;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }

    location /media {
        proxy_pass http://apps/media;
        access_log off;
        if (-f $request_filename) {
            expires 30d;
            break;
        }
    }
}
