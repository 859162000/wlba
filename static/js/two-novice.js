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
        var boy = $(document.body).height();
        $('#two-mov-ice').css({'height': boy});
        $('.two-buttonn,.chart1-button0').click(function(){
            $('#two-mov-ice').show();
            $('.mov').html('您已是网利宝用户，无需再注册');
             //window.location.href = '/activity/experience/mobile/';
        })
        $('.two-buttonu').click(function(){
            $('#two-mov-ice').show();
            $('.mov').html('扫下方服务号二维码，进行关注');
             //window.location.href = '/activity/experience/mobile/';
        })
        $('.ice-button').click(function(){
             $('#two-mov-ice').hide();
        })
        $('.two-buttonb').click(function(){
             verify()
        })
        verify()
        function verify(){
            $.ajax({
                url: '/api/id_validation/',
                type: 'POST',
                success: function (data) {
                    console.log(data)
                }

            })

        }///accounts/id_verify/




    });

})();