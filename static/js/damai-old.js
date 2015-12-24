(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery'], function ($) {
        var csrfSafeMethod, getCookie, sameOrigin,
            getCookie = function (name) {
                var cookie, cookieValue, cookies, i;
                cookieValue = null;
                if (document.cookie && document.cookie !== "") {
                    cookies = document.cookie.split(";");
                    i = 0;
                    while (i < cookies.length) {
                        cookie = $.trim(cookies[i]);
                        if (cookie.substring(0, name.length + 1) === (name + "=")) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                        i++;
                    }
                }
                return cookieValue;
            };
        csrfSafeMethod = function (method) {
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        };
        sameOrigin = function (url) {
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = "//" + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
        };
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });

        _getQueryStringByName = function (name) {
            var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
            if (result == null || result.length < 1) {
                return '';
            }
            return result[1];
        }
        //返回投票button
        $('.damaifu').on('click', function () {
            $('body,html').animate({scrollTop: 1257}, 600);
            return false
        });
        //请求票数接口
        $('.damai-buttonold').click(function () {
            redpack();
        })

        function redpack() {
            $.ajax({
                url: '/api/rock/finance/old_user/',
                type: "POST",
                data: {}
            }).done(function (damai) {
                console.log(damai);
                if (damai['ret_code'] == 0) {
                   $('.tishiyu').text('恭喜！您已获得网利宝摇滚之夜门票');
                } else if (damai['ret_code'] == 1006) {
                    $('.tishiyu').text('您已领过网利宝摇滚之夜门票');
                } else if (damai['ret_code'] == 1005) {
                    $('.tishiyu').text('很抱歉，门票已经发完了');
                } else if (damai['ret_code'] == 1004) {
                    $('.tishiyu').text('很抱歉，没有在预定的时间内购标');
                } else if (damai['ret_code'] == 1003) {
                    $('.tishiyu').text('很抱歉，门票已经发完了');
                } else if (damai['ret_code'] == 1001) {
                    $('.tishiyu').text('很抱歉，您投资没有满1000元');
                }


            });
        };
    });
})();