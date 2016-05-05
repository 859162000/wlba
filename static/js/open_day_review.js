(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(['jquery'],
        function($, re) {

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

            $('.advantage_wrap .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box4 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box5 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box6 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box7 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.body_wrap .slide_phone .small_box .img').click(function(){
                var data_src = $(this).attr('data-src');
                $(this).addClass('choose').siblings().removeClass('choose');
                $(this).parent().parent().find('.big_photo_img').attr('src',data_src);
            });



        })

}).call(this);