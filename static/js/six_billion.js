(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'underscore': 'lib/underscore-min',
            'Swiper':'lib/swiper_new_min'
        },
        shim: {
            'jquery.modal': ['jquery']

        }
    });
    require(['jquery','lib/countdown','Swiper'], function($, countdown) {

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

            var swiper = new Swiper('.swiper1', {
                nextButton: '.swiper-button-next',
                prevButton: '.swiper-button-prev',
                slidesPerView: 1
            });


            var endTime = new Date(2016,6,3,18,00,00);

            function getCurrentShowTimeSeconds(){
				var curTime = new Date();
				var ret = endTime.getTime() - curTime.getTime();
				//结束的时间减去现在的时间
				ret = Math.round(ret/1000);
				//把毫秒转化成秒

				return ret>=0 ? ret : 0 ;
				//ret大于等于0的话返回ret，如果不是返回0
				//如果倒计时结束，返回的结果是0
			}
            getCurrentShowTimeSeconds();
        })

}).call(this);