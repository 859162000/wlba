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
        //注册
        re.activityRegister.activityRegisterInit({
            registerTitle: '领取迅雷会员+现金红包',    //注册框标语
            isNOShow: '1',
            buttonFont: '立即注册'
        });
        //未登录时点击登入是状态
        $('.xunlei11dengru').on('click', function () {
            $('.denruxunlei').show();
            $('.dengxun11').hide();
        })
        //回到顶部开始
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

        //回到顶部结束

        //模态口高度
        var body_h = $('body').height();
        $('#small-zc').height(body_h);

        //关闭弹出框
        $('.first-xl-off2,.reg-btn').on('click', function () {
            $('#small-zc').hide();
            $('#xl-aug-login').hide();
            $('#xl-aug-success').hide();
            $('#xl-aug-prize').hide();
            $('#xl-aug-fail').hide();
        })


        var change = [];
        redpack('ENTER_WEB_PAGE');
        //领取会员提示
        $('.setp-btn').on('click', function () {

            if (change['ret_code'] == 4000) {
                $('#small-zc').show();
                $('#xl-aug-fail p').text('Sorry~您不符合领奖条件');
                $('#xl-aug-fail').show();
            } else if ($(this).hasClass('receive')) {
                //window.location.href = "/"
                $('body,html').animate({scrollTop: 0}, 600);
            } else {
                $('body,html').animate({scrollTop: 0}, 600);
                //$('#small-zc').show();
                //$('#xl-aug-login').show();
            }

        })

        //回到banner注册
        $('.setplogin').on('click', function () {
            $('#small-zc').hide();
            $('#xl-aug-login').hide();
            $('body,html').animate({scrollTop: 0}, 600);
            return false
        })
        //抽奖名单
        var str = '';
        $.ajax({
            url: "/api/xunlei/award/records/",
            type: "POST",
            async: false
        }).done(function (result) {
            for (var k = 0, len2 = result['data'].length; k < len2; k++) {
                var tel = result['data'][k]['phone'].substring(0, 3) + "******" + result['data'][k]['phone'].substring(9, 11);
                str += '<p>恭喜' + tel + '获得<span>' + result['data'][k]['awards'] + '元</span>红包</p>'
            }
            $('.long-p').append(str);
            $('.long-p p:odd').addClass('hight');
        });

        //无线滚动
        var timer, i = 1, j = 2;
        timer = setInterval(function () {
            scroll();
        }, 30)

        function scroll() {
            if (-parseInt($('.long-p').css('top')) >= $('.long-p p').height()) {
                $('.long-p p').eq(0).appendTo($('.long-p'));
                $('.long-p').css({'top': '0px'})
                i = 0
            } else {
                i++
                $('.long-p').css({'top': -i + 'px'})
            }

        }


        //游戏
        //1,跑马灯
        setInterval(function () {
            $('.ring').css({'background': 'url("/static/imgs/pc_activity/xunlei_one/ring-1.png") center center no-repeat'})
            setTimeout(function () {
                $('.ring').css({'background': 'url("/static/imgs/pc_activity/xunlei_one/ring-2.png") center center no-repeat'})
                setTimeout(function () {
                    $('.ring').css({'background': 'url("/static/imgs/pc_activity/xunlei_one/ring-3.png") center center no-repeat'})
                }, 250)
            }, 250)
        }, 500)

        //按钮

        if (change['left']) {
            $('#chance').text(' ' + change['left'] + ' ');
        } else if (change['left'] == 0) {
            $('#chance').text(' ' + change['left'] + ' ');
        } else {
            $('#chance').text(' ' + 3 + ' ');
        }
        $('.game-btn').on('mousedown', function () {
            $('.game-btn').addClass('game-btn-down')
        });
        $('.game-btn').on('mouseup', function () {
            redpack('ENTER_WEB_PAGE', function (data) {

                if (!$('.go-game').hasClass('noClick')) {
                    $('.game-btn').removeClass('game-btn-down');
                    if (data['ret_code'] == 4000) {
                        $('#small-zc').show();
                        $('#xl-aug-fail p').text('Sorry~您不符合抽奖条件');
                        $('#xl-aug-fail').show();
                    } else if (data['ret_code'] == 3003) {
                        if (change['left'] <= 0) {
                            $('#small-zc').show();
                            $('#xl-aug-fail p').text('Sorry~您的抽奖次数已用完')
                            $('#xl-aug-fail').show();
                        } else {
                            if (data['left'] == data['get_time']) {
                                game(data['get_time']);
                            } else {
                                game();
                            }

                        }
                    } else if (data['ret_code'] == 3000) {
                        $('body,html').animate({scrollTop: 0}, 600);
                        //$('#small-zc').show();
                        //$('#xl-aug-login').show();
                    }
                }
            })
        })
        function game(isGet) {
            $('.go-game').addClass('noClick');
            //按钮按下样式
            //手柄的样式
            setTimeout(function () {
                $('.side').addClass('side-down')
                setTimeout(function () {
                    $('.side').removeClass('side-down')
                }, 50)
                if (isGet) {
                    //成功调用
                    redpack('GET_AWARD');
                    //star('0' + change['amount']);
                    star(0088);
                } else {
                    //失败调用
                    redpack('IGNORE_AWARD');
                    star('0000');
                }
            }, 10)
        }


        //开始转动
        function star(a) {
            var time;
            time = setInterval(function () {
                $('.long-sum').animate({'bottom': '-1062px'}, 100, function () {
                    $('.long-sum').css({'bottom': '0px'})
                })
            }, 100)
            setTimeout(function () {
                for (var k = 0, len = a.length; k < len; k++) {
                    var g = 9 - a[k], b = k + 1;
                    $('.long-sum:eq(' + k + ')').css({'top': -g * 178 + 'px'})
                }
                clearInterval(time);
                $('.go-game').removeClass('noClick');
                $('#rmb').text(parseInt(change['amount']));
                $('#small-zc').show();
                if (a == '0000') {
                    var txt = ['你和大奖只是一根头发的距离', '天苍苍，野茫茫，中奖的希望太渺茫', '太可惜了，你竟然与红包擦肩而过'];
                    var ind = parseInt(Math.random() * 3);
                    $('#xl-aug-success').hide();
                    $('#xl-aug-prize p').text(txt[ind]);
                    $('#xl-aug-prize').show();
                } else {
                    $('#xl-aug-prize').hide();
                    $('#xl-aug-success').show();
                }
            }, 3000)
            $('.long-sum').css({'top': ''});
            $('#chance').text(' ' + change['left'] + ' ')
        }


        //抽奖请求
        function redpack(sum, callback) {
            $.ajax({
                url: "/api/xunlei/award/",
                type: "POST",
                data: {action: sum},
                async: false
            }).done(function (data) {
                change = data;
                $('#chance').text(change['left']);

                callback && callback(data);

            });
        }
    });
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
    getCode();
}).call(this);
