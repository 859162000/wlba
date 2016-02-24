(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery', 'activityRegister'], function ($, re) {
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
        //注册
        re.activityRegister.activityRegisterInit({
            registerTitle: '领取迅雷会员+现金红包',    //注册框标语
            isNOShow: '1',
            buttonFont: '立即注册',
            hasCallBack: true,
            callBack: function () {
                if ($('#register_submit').hasClass('buttom-mm')) {
                    if (getQueryString('referfrom')) {
                        var refer = getQueryString('referfrom');
                        window.location.href = "http://act.vip.xunlei.com/vip/cooplogin/?coop=wanglibao&referfrom=" + refer;
                    }

                } else {
                    history.go(0);
                }


            }
        });
        //固定回到顶部,
        function backtop(box) {
            var k = document.body.clientWidth,
                e = box.width();
            q = k - e;
            w = q / 2;
            r = e + w;
            a = r + 20 + 'px';
            return a;
        }

        var left2;
        left2 = backtop($(".setp-content"));
        //浏览器大小改变触发的事件
        window.onresize = function () {
            left2 = backtop($(".setp-content"));
        };
        //赋值
        $('.xl-backtop').css({'left': left2});

        //显示微信二维码
        $('#xl-weixin').on('mouseover', function () {
            $('.erweima').show();
        });

        $('#xl-weixin').on('mouseout', function () {
            $('.erweima').hide();
        })

        //返回顶部
        $(window).scroll(function () {
            if ($(document).scrollTop() > 0) {
                $(".xl-backtop").fadeIn();
            } else {
                $('.xl-backtop').stop().fadeOut();
            }
        });

        $('.backtop').on('click', function () {
            $('body,html').animate({scrollTop: 0}, 600);
            return false
        })
        //回到banner注册
        $('.buttonxunlei1,.buttonxunlei3,.buttonxunlei5,.buttonxunlei').click(function () {

            $('body,html').animate({scrollTop: 0}, 600);
            return false

        })
        //路径$("#index_01").attr("src","images/index_01_1.jpg");
        //效果
        var click = false;
        $('#vertical').find('a').click(function () {
             if (click) {
                    return false;
                } else {
                    click = true;
                }
            $.ajax({
                url: "/api/activity/reward/",
                type: "POST",
                data:{ activity:'xunlei'},
                async: false
            }).done(function (data) {
                console.log(data)

            });
            var self = $(this),
                img = self.find('.imgg');
            img.animate({'width': 0}, 500, function () {
                $(this).hide().next().show();
                $(this).next().animate({'width': '261px'}, 300, function () {
                    $('#vertical').find('a').removeClass('xun');
                    setTimeout(function () {
                        self.find('.info').animate({'width': 0}, 300, function () {
                            $(this).hide();
                            img.show();
                            img.animate({'width': '261px'}, 300,function(){
                                 click = false;
                            });
                        });

                    }, 3000);

                });

            });

        })

        //function chances() {


        //}



        //登入框穿参数
        function getQueryString(name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return unescape(r[2]);
            }
            return null;
        }

        var token = getQueryString('promo_token'),
            xid = getQueryString('xluserid'),
            timer = getQueryString('time'),
            sig = getQueryString('sign'),
            name = getQueryString('nickname');
        //alert(token+','+xid+','+timer+','+sig+','+name);
        if ($('.denelu-form').hasClass('dengruhou')) {
            $.ajax({
                type: "POST",
                url: "/activity/thunder/binding/",
                data: {
                    'promo_token': token,
                    'xluserid': xid,
                    'time': timer,
                    'sign': sig,
                    'nickname': name

                },
                success: function (data) {
                    if (data.ret_code == 10002 || data.ret_code == 10000) {
                        $('.xunshang1').text('恭喜已完成网利宝注册');
                        $('.xunshang2').text('并与您的迅雷账号绑定成功');
                        $('.xunleiten1').css({display: 'block'});
                        $('.xunleiten2').css({display: 'block'});
                    } else {
                        $('.xunshang1').text('恭喜已完成网利宝注册');
                        $('.xunleiten2').css({display: 'block'});

                    }

                },
                error: function () {

                }
            });
            getCode();

        }
        var xluserid = getQueryString('xluserid'),
            referfrom = getQueryString('referfrom')
        $.ajax({
            url: '/api/coop_pv/' + token + '/?source=pv_wanglibao&ext=' + xluserid + '&ext2=' + referfrom,
            type: "GET"
        })
        function getCode() {//得到用户信息的二维码
            var original_id = document.getElementById("original_id").value;
            var code = document.getElementById("weixin_code").value;
            $.ajax({
                type: "GET",
                url: "/weixin/api/generate/qr_scene_ticket/",
                data: {"original_id": original_id, "code": code},//c:gh_32e9dc3fab8e, w:gh_f758af6347b6;code:微信关注渠道
                success: function (data) {
                    $("#erweimaxunlei11").html("<img src='" + data.qrcode_url + "' />");
                },
                error: function () {
                    window.location.href = "/weixin/jump_page/?message=出错了";
                }
            });
        }
    });


}).call(this);
