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

        $.ajax({
            url: '/api/activity/chefangdai/',
            type: 'post',
            success: function (data) {
                //if(data.ret_code=='1000'){
                //    window.location.href = '/accounts/login/?promo_token=sy&next=/activity/august_phone/?promo_token=sy'
                //}else if(data.ret_code=='1'||data.ret_code=='1001'||data.ret_code=='1002'){
                //    $('.popup_box .main .textairport').text(''+data.message+'');
                //    $('.popup_box').show();
                //}else if(data.ret_code=='0'){
                //    if(data.tag=='标记成功'){
                //        window.location.href = '/p2p/list/?promo_token=sy'
                //    }else{
                //        $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                //        $('.popup_box').show();
                //    }
                //}
                $('.luck_title_wrap dl dt').text(data.message);
                for(var i=0;i<data.rewards_list.luck_list.length;i++){

                }
            }
        })

        var speed = 100;//速度
        var time = "";//创建一个定时器
          $(function () {
            $(".choujiang").click(function() {//触发事件
              $("#msgBox").fadeOut();
              doIt(1,1)//直接传入初始化参数，防止再次点击位置不对
            });
          });
          function doIt(t,i){//执行循环主方法
            time = setInterval(function () {
              i++;
              if (i > 8) {i = 1;t++;}
              $(".cj").removeClass("cur");
              $("#cj"+i).addClass("cur");
              getLb(t,i);
            }, speed);
          }
          function getLb(t,i){//中奖之后的处理
            console.log(t);
            console.log(i);
            if (t == 3) {
              if (i == 1) {//此处的i为设定的中奖位置，也可用ajax去请求获得
                clearInterval(time);
                $("#msgBox").fadeIn().find("#text").html("恭喜你中奖了:第"+i+"！");
              }
            }
          }


        })

}).call(this);