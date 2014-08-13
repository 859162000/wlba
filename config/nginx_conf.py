from vender.nginxparser import dumps


def generate_conf(apps, port='80'):
    conf = [
        ['proxy_cache_path', '/var/cache/nginx levels=1:2 keys_zone=static-cache:8m max_size=1000m inactive=600m'],
        ['proxy_temp_path', '/var/cache/tmp'],

        [['server'], [
            ['listen', '80'],
            ['return', '301 https://$host$request_uri'],
        ]],
        [['server'], [
            ['listen', '443 ssl'],
            ['server_name', 'localhost'],
            ['ssl_certificate', '/etc/nginx/ssl/wanglibao.crt'],
            ['ssl_certificate_key', '/etc/nginx/ssl/wanglibao.key'],
            ['ssl_protocols', 'SSLv3 TLSv1 TLSv1.1 TLSv1.2'],
            ['ssl_ciphers', 'RC4:HIGH:!aNULL:!MD5'],
            ['ssl_session_cache', 'shared:SSL:10m'],
            ['ssl_session_timeout', '10m'],

            [['location', '/'], [
                ['proxy_pass', 'http://apps'],
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
        ]],
        [['upstream apps'], [('server', name + ':' + port) for name in apps]]
    ]

    return dumps(conf)
