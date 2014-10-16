from vender.nginxparser import dumps


def generate_conf(apps, upstream_port='80', listen_on_80=True):
    conf = [
        ['proxy_cache_path', '/var/cache/nginx levels=1:2 keys_zone=static-cache:8m max_size=1000m inactive=600m'],
        ['proxy_temp_path', '/var/cache/tmp'],
        ['add_header', 'X-Cached $upstream_cache_status']
    ]

    if listen_on_80:
        conf += [
            [['server'], [
                ['listen', '80'],
                ['server_name', 'www.wanglibao.com staging.wanglibao.com pre.wanglibao.com'],
                ['return', '301 https://$host$request_uri'],
            ]],
            [['server'], [
                ['listen', '80'],
                ['server_name', 'wanglibao.com'],
                ['return', '301 https://www.wanglibao.com$request_uri'],
            ]],
            [['server'], [
                ['listen', '443 ssl'],
                ['server_name', 'wanglibao.com'],
                ['ssl_certificate', '/etc/nginx/ssl/wanglibao.crt'],
                ['ssl_certificate_key', '/etc/nginx/ssl/wanglibao.key'],
                ['ssl_protocols', 'SSLv3 TLSv1 TLSv1.1 TLSv1.2'],
                ['ssl_ciphers', 'RC4:HIGH:!aNULL:!MD5'],
                ['ssl_session_cache', 'shared:SSL:10m'],
                ['ssl_session_timeout', '10m'],
                ['return', '301 https://www.wanglibao.com$request_uri'],
            ]]
        ]

    conf += [
        [['server'], [
            ['listen', '443 ssl'],
            #['server_name', 'localhost'],
            ['server_name', 'www.wanglibao.com pre.wanglibao.com staging.wanglibao.com'],
            ['ssl_certificate', '/etc/nginx/ssl/wanglibao.crt'],
            ['ssl_certificate_key', '/etc/nginx/ssl/wanglibao.key'],
            ['ssl_protocols', 'SSLv3 TLSv1 TLSv1.1 TLSv1.2'],
            ['ssl_ciphers', 'RC4:HIGH:!aNULL:!MD5'],
            ['ssl_session_cache', 'shared:SSL:10m'],
            ['ssl_session_timeout', '10m'],

            [['location', '/'], [
                ['proxy_pass', 'http://apps'],
                ['proxy_set_header', 'Host $host'],
                ['proxy_set_header', 'X-Real-IP $remote_addr'],
                ['proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for']
            ]],

            [['location', '/nginx_status'], [
                ['stub_status', 'on'],
                ['access_log', 'off'],
            ]],

            [['location', '/static'], [
                ['proxy_pass', 'http://apps/static'],
                ['proxy_cache', 'static-cache'],
                ['proxy_cache_valid', '200 302 60m'],
                ['proxy_cache_valid', '404 1m'],
            ]],

            [['location', '/media'], [
                ['proxy_pass', 'http://apps/media'],
                ['proxy_cache', 'static-cache'],
                ['proxy_cache_valid', '200 302 60m'],
                ['proxy_cache_valid', '404 1m'],
            ]],
        ]],
        [['upstream apps'], [('server', name + ':' + upstream_port) for name in apps]]
    ]

    return dumps(conf)
