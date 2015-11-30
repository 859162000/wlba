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

        var arrPos = new Array();
        window.onload = function () {
            //点击抽奖

            lottery.init('lottery');
            $(".prize-mingdan").on('click', '.jiang-button2', function () {
                if (click) {
                    return false;
                } else {
                    click = true;
                }
                if (change['left'] == 0) {
                    return;
                }
                redpack({
                    'action': "POINT_AT",
                    'activity': "thanks_given",
                    'level': "5000+"
                }, function () {
                    if (change['left'] == 0) {
                        $('.jiang-button').removeClass("jiang-button2");
                        $('.jiang-button').addClass("jiang-button1");
                        $('.prize-mingdan .prize-ri p').html('您没有抽奖机会');
                        if (change['reward'] == null) {
                            return;
                        }
                        //return;
                    } else {
                        $('.app-jihui').text(change['left']);
                    }

                    lottery.speed = 100;
                    roll();


                })
            });
            //抽奖2
            var onclick = false;
            $('.thanks2').on('click', function () {
                if (onclick) {
                    return false;
                } else {
                    onclick = true;
                }
                if (change['left'] == 0) {
                    return;
                }
                redpack({
                    'action': "POINT_AT",
                    'activity': "thanks_given",
                    'level': "5000-"
                }, function () {
                    if (change['left'] == 0) {
                        $('.thanks').removeClass("thanks2");
                        $('.thanks').addClass("thanks1");
                        $('.main-thank .prize-ri1 p').html('您没有抽奖机会');
                        if (change['reward'] == null) {
                            return;
                        }
                    } else {
                        $('.main-thank .prize-ri1 p span').text(change['left']);
                    }
                    $('.hongxi').show();
                    $('#thankgi-thanks2 ').text(change['reward']);

                    onclick = false;
                })
            })
            //banner动画
            document.getElementsByTagName('body')[0].onmousemove = function (e) {
                var x = e.clientX || window.event.clientX, y = e.clientY || window.event.clientY;
                //判断鼠标运行方向
                var direction = '';
                if (arrPos.length > 0) {
                    if (x > arrPos[0][0]) {
                        if (y == arrPos[0][1]) {
                            //direction = '右';direction = $('.bannerdong').css("left", "260px");
                        }
                        else {
                            if (y > arrPos[0][1]) {
                                direction = '右下';
                            }
                            else direction = '右上';
                        }
                    }
                    else {
                        if (x == arrPos[0][0]) {
                            if (y < arrPos[0][1]) {
                                direction = '上';
                                direction = $('.bannerdong').css("top", "-15px");
                            }
                            else {
                                if (y > arrPos[0][1]) {
                                    direction = '下';
                                    direction = $('.bannerdong').css("top", "0px");
                                }
                            }
                        }
                        else {
                            if (y == arrPos[0][1]) {
                                //direction = '左';
                                // direction = $('.bannerdong').css("left", "100px");
                            }
                            else {
                                if (y > arrPos[0][1]) direction = '左上';
                                else direction = '左下';
                            }
                        }
                    }
                }

                if (arrPos.length < 1) arrPos.push(Array(x, y));
                else {
                    arrPos[0][0] = x;
                    arrPos[0][1] = y;
                    //document.getElementById('direction').innerHTML = direction;
                    $('#direction .ww').css(direction);

                }
            }
        }
        //弹层
        var h = $('.thanksgiving').height();
        $('.thanksgiving-kuang').css("height", h);
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

        //固定回到顶部
        function backtop() {
            var k = document.body.clientWidth,
                a = k - 100
            return a;
        }

        var left2 = backtop();
        //浏览器大小改变触发的事件
        window.onresize = function () {
            left2 = backtop();
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
        //规则显示隐藏
        $('.prize-title1 .title1-a').on('click', function () {
            $('.title1-guizhe').slideToggle();
        })
        $('.investment-title1 .title1-a').on('click', function () {
            $('.title1-guizhe1').slideToggle();
        })
        var change = [];
        redpack({
            'action': "GET_REWARD_INFO",
            'activity': "thanks_given"
            //'level': "5000+"
        }, function () {
            if (change['left'] == 0) {
                $('.jiang-button').removeClass("jiang-button2");
                $('.jiang-button').addClass("jiang-button1");
                $('.prize-mingdan .prize-ri p').html('您没有抽奖机会');
            } else {
                $('.app-jihui').text(change['left']);
            }
        });
        redpack({
            'action': 'GET_REWARD_INFO',
            'activity': "thanks_given",
            'level': "5000-"
        }, function () {
            if (change['left'] == 0) {
                $('.thanks').removeClass("thanks2");
                $('.thanks').addClass("thanks1");
                $('.main-thank .prize-ri1 p').html('您没有抽奖机会');
            } else {
                $('.main-thank .prize-ri1 p span').text(change['left']);
            }


        });
        //名单
        var str = '';
        if (change['ret_code'] != 1000) {
            redpack({
                    'action': 'GET_REWARD',
                    'activity': "thanks_given",
                    'level': "5000+"
                },
                function () {


                    for (var k = 0, len2 = change['phone'].length; k < len2; k++) {
                        var tel = change['phone'][k].substring(0, 3) + "******" + change['phone'][k].substring(9, 11);

                        str += '<p>恭喜' + tel + '获得<span>' + change['rewards'][k] + '</span></p>';

                    }

                    $('.long-p').append(str);
                });
        }

        //抽奖
        var arr = ['扫地机器人', '感恩节200元现金红包', '感恩节1.8%加息券', '感恩节10元现金红包', 'iPhone6s plus', '感恩节2.2%加息券', 'beats头戴式耳机', '感恩节80元现金红包', '感恩节1%加息券', '感恩节400元现金红包', '霍尼韦尔空气净化器', '感恩节1.5%加息券', '感恩节600元现金红包', '一年迅雷会员'];
        arr.indexof = function (value) {
            var a = this;
            for (var i = 0; i < a.length; i++) {
                if (a[i] == value)
                    return i;
            }
        }
        //alert(arr.indexof('200元现金红包'));


        var lottery = {
            index: -1,	//当前转动到哪个位置，起点位置
            count: 0,	//总共有多少个位置
            timer: 0,	//setTimeout的ID，用clearTimeout清除
            speed: 20,	//初始转动速度
            times: 0,	//转动次数
            cycle: 50,	//转动基本次数：即至少需要转动多少次再进入抽奖环节
            prize: -1,	//中奖位置
            init: function (id) {
                if ($("#" + id).find(".lottery-unit").length > 0) {
                    $lottery = $("#" + id);
                    $units = $lottery.find(".lottery-unit");
                    this.obj = $lottery;
                    this.count = $units.length;
                    $lottery.find(".lottery-unit-" + this.index).children().addClass("active");
                }
                ;
            },
            roll: function () {
                var index = this.index;
                var count = this.count;
                var lottery = this.obj;
                $(lottery).find(".lottery-unit-" + index).children().removeClass("active");
                index += 1;
                if (index > count - 1) {
                    index = 0;
                }
                ;
                $(lottery).find(".lottery-unit-" + index).children().addClass("active");
                this.index = index;
                return false;
            },
            stop: function (index) {
                this.prize = index;
                this.index = 6;
                return false;
            }
        };

        function roll() {
            lottery.times += 1;
            lottery.roll();
            if (lottery.times > lottery.cycle + 10 && lottery.prize == lottery.index) {
                clearTimeout(lottery.timer);
                lottery.prize = -1;
                lottery.times = 0;
                //奖品弹出位子
                $('.thanksgiving-kuang').css('display', 'block');
                $('.kuang-tidhi').css('display', 'block');
                $('.imgx').on('click', function () {
                    $('.active1').removeClass("active");
                    $('.thanksgiving-kuang').css('display', 'none');
                    $('.kuang-tidhi').css('display', 'none');
                });


                click = false;
            } else {
                if (lottery.times < lottery.cycle) {
                    lottery.speed -= 10;
                } else if (lottery.times == lottery.cycle) {
                    //奖品位置
                    //var index = Math.random() * (lottery.count) | 0;
                    var index = arr.indexof(change['reward'])
                    lottery.prize = index;

                } else {
                    if (lottery.times > lottery.cycle + 10 && ((lottery.prize == 0 && lottery.index == 7) || lottery.prize == lottery.index + 1)) {
                        lottery.speed += 110;
                    } else {
                        lottery.speed += 20;
                    }
                }
                if (lottery.speed < 40) {
                    lottery.speed = 40;
                }
                ;

                lottery.timer = setTimeout(roll, lottery.speed);
            }
            return false;
        }

        var click = false;

        function redpack(data, callback) {
            $.ajax({
                url: '/api/activity/reward/',
                type: "POST",
                data: data,
                async: false
            }).done(function (data) {
                change = data;
                callback && callback(data);


                // $('.app-jihui1').text(change['left']);

                //if (change['is_first'] == false) {
                //    $('.kuang-tidhi').addClass("kuang-tidhi12");
                //} else if (change['is_first'] == true) {
                //    $('.kuang-tidhi').removeClass("kuang-tidhi12");
                //}

                $('#app-jiangli').text(change['reward']);
            });
        }


    });

})();