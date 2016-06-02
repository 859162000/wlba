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

            /*轮播图*/
            var swiper = new Swiper('.swiper1', {
                nextButton: '.swiper-button-next',
                prevButton: '.swiper-button-prev',
                slidesPerView: 1
            });
            /*轮播图结束*/

            /*指定范围倒计时*/
            var time_intervalId;
            var curShowTimeSeconds = 0;
			//现在倒计时需要有多少秒
            var endTime = new Date(2016,5,3,18,00,00);
            //回头这里改成 2016,5,3,20,00,00

            var timestamp = Date.parse(new Date());
            //获得当前时间戳
            var timerFunction = function () {
                timestamp = Date.parse(new Date());
                if(timestamp>='1464919200000'){
                //2016年6月3日 10:00-18:00



                    curShowTimeSeconds = getCurrentShowTimeSeconds();
                    var hours = parseInt(curShowTimeSeconds/3600);
                    var minutes = parseInt((curShowTimeSeconds - hours * 3600)/60);
                    var seconds = curShowTimeSeconds % 60;

                    $('.countdown_time .time_1').text(parseInt(hours/10));
                    $('.countdown_time .time_2').text(parseInt(hours%10));

                    $('.countdown_time .time_3').text(parseInt(minutes/10));
                    $('.countdown_time .time_4').text(parseInt(minutes%10));

                    $('.countdown_time .time_5').text(parseInt(seconds/10));
                    $('.countdown_time .time_6').text(parseInt(seconds%10));
                    if(Date.parse(new Date())>'1464948000000'){
                        clearInterval(time_intervalId);
                    }


                $('.countdown_wrap').show();
                $('.project_wrap').show();
                $('.project_wrap .project_box .meng_layer').hide();
                }else{
                    $('.countdown_wrap').hide();
                    $('.project_wrap').show();
                    $('.project_wrap .project_box').append('<div class="meng_layer"></div>');

                }
            }
            time_intervalId = setInterval(timerFunction, 1000);

            function getCurrentShowTimeSeconds(){
				var curTime = new Date();
				var ret = endTime.getTime() - curTime.getTime();
				//结束的时间减去现在的时间
				ret = Math.round(ret/1000);
				//把毫秒转化成秒

				return ret>=0 ? ret : 0;
				//ret大于等于0的话返回ret，如果不是返回0
				//如果倒计时结束，返回的结果是0
			}
            /*指定范围倒计时结束*/



        })

}).call(this);