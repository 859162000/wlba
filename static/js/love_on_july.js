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


            function fmoney(s, type) {
                if (/[^0-9\.]/.test(s))
                    return "0";
                if (s == null || s == "")
                    return "0";
                s = s.toString().replace(/^(\d*)$/, "$1.");
                s = (s + "00").replace(/(\d*\.\d\d)\d*/, "$1");
                s = s.replace(".", ",");
                var re = /(\d)(\d{3},)/;
                while (re.test(s))
                    s = s.replace(re, "$1,$2");
                s = s.replace(/,(\d\d)$/, ".$1");
                if (type == 0) {// 不带小数位(默认是有小数位)
                    var a = s.split(".");
                    if (a[1] == "00") {
                        s = a[0];
                    }
                }
                return s;
            }

            $.ajax({
                url: '/api/july_reward/fetch/',
                type: 'post',
                success: function (json) {
                    var rankingList = [];
                    var json_one;
                    if(json.dayranks.length>0){
                        for(var i=0; i<json.dayranks.length; i++) {

                            json_one = json.dayranks[i];
                            if (json_one != '') {
                                var number = fmoney(json_one.amount__sum, 1);

                                if (i < 3) {
                                    if (i == 0) {
                                        rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/pc_activity/love_on_july/section_3_img10.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num"><span class="money_num1">'+number+'元</span></div></div>'].join(''));
                                    } else if (i == 1) {
                                        rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/pc_activity/love_on_july/section_3_img11.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num"><span class="money_num2">'+number+'元</span></div></div>'].join(''));
                                    } else if (i == 2) {
                                        rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/pc_activity/love_on_july/section_3_img12.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num"><span class="money_num3">'+number+'元</span></div></div>'].join(''));
                                    }

                                } else {

                                }
                            }
                        }
                        $('.now_main').html(rankingList.join(''));
                    }

                },error: function(data1){

                }
            })


        var oDate = new Date(); //实例一个时间对象；
        var nian = oDate.getFullYear();   //获取系统的年；
        var yue = oDate.getMonth()+1;   //获取系统月份，由于月份是从0开始计算，所以要加1
        var ri = oDate.getDate(); // 获取系统日，
        var shi = oDate.getHours(); //获取系统时，
        var fen = oDate.getMinutes(); //分
        oDate.getSeconds(); //秒

        function bu_ling(s) {
            return s < 10 ? '0' + s: s;
        }

        $('#act_time').text('截止 '+nian+'.'+bu_ling(yue)+'.'+bu_ling(ri)+' '+bu_ling(shi)+':'+bu_ling(fen)+'');
        })

}).call(this);