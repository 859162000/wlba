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
            registerTitle: '领取迅雷会员+现金红包 ',    //注册框标语
            isNOShow: '1',
            buttonFont: '立即注册',
            callBack: function(){
                getCode();
            }
        });
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
        //点击显示规则
        $('.xuntenxia').on('click', function () {
            $(".ten-rule").slideToggle();

        });
        $('#guizhexunlei').on('click', function () {
            $(".xianshi").slideToggle();

        });
        //未登录时点击登入是状态
        $('.xunlei11dengru').on('click', function () {
             $('.denruxunlei').show();
             $('.dengxun11').hide();
        })

        //关闭弹出框
        var change = [];
        redpack('ENTER_WEB_PAGE');
        var times = 0;
        $('.first-xl-off2,.reg-btn').on('click', function () {
            //window.location.reload();
            if (times == 0) {
                $('.left-box').addClass("small-box-open");
            } else if (times >= 1) {
                $('.right-box').addClass("small-box-open1");
            }
            times++;
            if (change['ret_code'] == 4000) {
                $('.left-box').removeClass("small-box-open");
                $('.right-box').removeClass("small-box-open1");
            }
            if (change['ret_code'] == 3000) {
                $('.left-box').removeClass("small-box-open");
                $('.right-box').removeClass("small-box-open1");
            }
            if (change['left'] == 0) {
                $('.center-box').addClass("big-box-open");
                $('.left-box').addClass("small-box-open");
                $('.right-box').addClass("small-box-open1");
            } else {
                $('.center-box').removeClass("big-box-open");
            }

            $('#small-zc').hide();
            $('#xl-aug-login').hide();
            $('#xl-aug-success11').hide();
            $('#xl-aug-prize').hide();
            $('#xl-aug-fail').hide();
        })


        //回到banner注册
        $('.setplogin').on('click', function () {
            $('#small-zc').hide();
            $('#xl-aug-login').hide();
            $('body,html').animate({scrollTop: 0}, 600);
            return false
        })

        //金币落下的效果

        var timer;
        timer = setInterval(function () {
            $('.money').animate({'top': '281px', 'left': '43px', 'display': 'none'}, 500, function () {
                $('.money').css({'top': '135px', 'left': '-97px', 'display': 'block'})
            })
        }, 1000)

        //送加息 会员
        $('.ten-txtbutn').on('click', function () {
            if (change['ret_code'] == 4000) {
                $('#small-zc').show();
                $('#xl-aug-fail p').text('Sorry~您不符合领奖条件');
                $('#xl-aug-fail').show();
            } else if ($(this).hasClass('received')) {
                window.location.href = "/"
            }
            else if ($(this).hasClass('receiveg')) {
                window.location.href = "/pay/banks/"
            } else if ($(this).hasClass('receiveh')) {
                window.location.href = "/p2p/list/"
            } else {
                $('#small-zc').show();
                $('#xl-aug-login').show();
            }

        })

        //回到banner注册
        $('.setplogin').on('click', function () {
            $('#small-zc').hide();
            $('#xl-aug-login').hide();
            $('body,html').animate({scrollTop: 0}, 600);
            return false
        })
        if (change['left'] == 2) {
            $('.left-box').addClass("small-box-open");
        } else if (change['left'] == 1) {
            $('.left-box').addClass("small-box-open");
            $('.right-box').addClass("small-box-open1");
        } else if (change['left'] == 0) {
            $('.center-box').addClass("big-box-open");
            $('.left-box').addClass("small-box-open");
            $('.right-box').addClass("small-box-open1");
        }
        else {
            $('.center-box').removeClass("big-box-open");
        }
        //宝箱点击
        $('.open-box-btn').on('click', function () {
            redpack('ENTER_WEB_PAGE', function (data) {
                if (data['ret_code'] == 4000) {
                    $('.center-box').removeClass("big-box-open");
                    $('#small-zc').show();
                    $('#xl-aug-fail p').text('Sorry~您不符合抽奖条件');
                    $('#xl-aug-fail').show();
                } else if (data['ret_code'] == 3003) {
                    $('.center-box').addClass("big-box-open");
                    if (change['left'] <= 0) {
                        $('#small-zc').show();
                        $('#xl-aug-fail p').text('Sorry~您的抽奖次数已用完')
                        $('#xl-aug-fail').show();
                    } else {
                        $('.center-box').addClass("big-box-open");
                        if (data['left'] == data['get_time']) {
                            game(data['get_time']);
                        } else {
                            game();
                            $('.center-box').addClass("big-box-open");
                        }

                    }
                } else if (data['ret_code'] == 3000) {
                    $('#small-zc').show();
                    $('#xl-aug-login').show();
                    $('.center-box').addClass("big-box-open");
                }
            })
        })


        function game(isGet) {

            if (isGet) {
                //成功调用
                redpack('GET_AWARD');
                star('0' + change['amount']);
            } else {
                //失败调用
                redpack('IGNORE_AWARD');
                star();
            }
        }


        //提示语
        function star() {
            $('#rmb').text(parseInt(change['amount']));
            $('#small-zc').show();
            if (change['ret_code'] == 3002) {
                $('.center-box').addClass("big-box-open");
                var txt = ['佛说：前世的500次回眸才换得一次中奖，淡定', '奖品何时有，把酒问青天', '大奖下回见，网利宝天天见'];
                var ind = parseInt(Math.random() * 3);
                $('#xl-aug-success11').hide();
                $('#xl-aug-prize p').text(txt[ind]);
                $('#xl-aug-prize').show();

            } else if (change['ret_code'] == 3001) {
                $('#xl-aug-prize').hide();
                var xii = ['人世间最美好的事情莫过于如此，0.5%加息券', '人品大爆发，0.5%加息券', '终于等到你，还好我没放弃，0.5%加息券'];
                var shu = parseInt(Math.random() * 3);
                $('#xl-aug-success11 p .xl-aug').text(xii[shu]);
                $('#xl-aug-success11').show();
            }

        }

        //请求宝箱接口
        function redpack(sum, callback) {
            $.ajax({
                url: "/api/xunlei/award/action/",
                type: "POST",
                data: {action: sum},
                async: false
            }).done(function (data) {
                change = data;
                callback && callback(data);


            });
        }
        //添加奖品份数
        $('#jianli').html(change['award']);

    });
}).call(this);
