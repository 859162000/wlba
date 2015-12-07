var version = navigator.userAgent
var index1 = version.indexOf("wlbAPP/");
if (index1 === -1) {
    $('.appjiang-button').addClass("appjiang-button1")
    //$('.appprize-mingdan .appjiang-ri p').html('升级为最新版APP即可抽奖，或前往网利宝官方网站').css('color', '#f6d564');
    $('.appprize-mingdan .appjiang-ri p').html('升级为最新版APP即可抽奖，或前往网利宝官方网站').css({
            'text-align': 'left',
            'color': '#f6d564',
            'margin-left': '18px'
        }
    )
    ;

    $('.yellow1-main .appjiang-ri p').html('升级为最新版APP即可抽奖，或前往网利宝官方网站').css('color', '#12d0f1');
    $('.appprize-mingdan .appjiang-ri .jiang-a,.yellow1-main .appjiang-ri .jiang-a').hide();
    $('.app-thanks').hide();
    $('.app-thanksbu').addClass("app-thanksbu1")
    $('.app-thanks01').show().html('理财专区即可投资');
}
function Down(ele) {
    var curHeight = ele.height();
    var autoHeight = ele.css('height', 'auto').height();
    if (!ele.hasClass('down')) {
        ele.height(curHeight).animate({height: autoHeight}, 500, function () {
            ele.addClass('down')
        });
    } else {
        ele.height(curHeight).animate({height: 0}, 500, function () {
            ele.removeClass('down')
        });
    }
}

$(".thanks-main p .title1-a").on("click", function () {
    Down($(".app-thanks-giv"));
});
$(".thanks-main1 p .title1-a").on("click", function () {
    Down($(".app-thanks-giv1"));
});

var login = false;
//$('.appjiang-button').html(123)
wlb.ready({
    app: function (mixins) {
        $('.appprize-mingdan .appjiang-ri .jiang-a,.app-thanks,.yellow1-main .appjiang-ri .jiang-a').click(function () {
            mixins.jumpToManageMoney();
        })

        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                login = false;
                $('.appprize-mingdan .appjiang-ri p').html('');
                $('.appjiang-button').removeClass('appjiang-button2');
                $('.appjiang-button').addClass("appjiang-button1").click(
                    function () {
                        mixins.loginApp({refresh: 1}, function () {
                            $('.appjiang-button').removeClass('appjiang-button1').addClass("appjiang-button2");
                        });
                    }
                );
                $('.yellow1-main .appjiang-ri p').html('');
                $('.app-thanksbu').removeClass('.app-thanksbu2').addClass("app-thanksbu1").click(
                    function () {
                        mixins.loginApp({refresh: 1}, function () {
                            $('.app-thanksbu').removeClass('app-thanksbu1').addClass("app-thanksbu2");
                        });
                    }
                );

            } else {
                login = true;
                org.ajax({
                    url: '/accounts/token/login/ajax/',
                    type: 'post',
                    data: {
                        token: data.tk,
                        secret_key: data.secretToken,
                        ts: data.ts
                    },
                    success: function (data1) {
                        redpack({
                            'action': "GET_REWARD_INFO",
                            'activity': "thanks_given",
                            'level': "5000+"
                        }, function (da) {
                            //$('.appprize-mingdan .appjiang-ri p span').text(da['left']);
                            if (da['left'] == 0) {
                                $('.appjiang-button').removeClass("appjiang-button2").addClass("appjiang-button1");
                                $('.appprize-mingdan .appjiang-ri p').html('您没有抽奖机会');
                            } else {
                                $('.appprize-mingdan .appjiang-ri p span').text(da['left']);
                            }
                        });
                        function redpack2(d) {
                            if (d['left'] == 0) {
                                $('.app-thanksbu').removeClass("app-thanksbu2").addClass("app-thanksbu1");
                                $('.yellow1-main .appjiang-ri p').html('您没有抽奖机会');
                            } else {
                                $('.yellow1-main .appjiang-ri p span').html(d['left']);
                            }
                        }

                        redpack({
                            'action': 'GET_REWARD_INFO',
                            'activity': "thanks_given",
                            'level': "5000-"
                        }, redpack2);
                    }
                    //error: function(data){
                    //  $('#log3').html('ajax error');
                    //  window.location.href = $("input[name='next']").val() + "nologin/";
                    //}
                })


            }
            //$('.appjiang-button')
            //if (login) {

            var change = [];
//抽奖
            var arr = ['扫地机器人', '感恩节200元现金红包', '感恩节1.8%加息券', '感恩节10元现金红包', 'iPhone6s plus', '感恩节2.2%加息券', 'beats头戴式耳机', '感恩节80元现金红包', '感恩节1%加息券', '感恩节400元现金红包', '霍尼韦尔空气净化器', '感恩节1.5%加息券', '感恩节600元现金红包', '一年迅雷会员'];
            arr.indexof = function (value) {
                var a = this;
                for (var i = 0; i < a.length; i++) {
                    if (a[i] == value)
                        return i;
                }
            }
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
                        $lottery.find(".lottery-unit-" + this.index).children().first().addClass("active");
                    }
                    ;
                },
                roll: function () {
                    var index = this.index;
                    var count = this.count;
                    var lottery = this.obj;
                    $(lottery).find(".lottery-unit-" + index).children().first().removeClass("active");
                    index += 1;
                    if (index > count - 1) {
                        index = 0;
                    }
                    ;
                    $(lottery).find(".lottery-unit-" + index).children().first().addClass("active");
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
                    $('.app-jiangshow').css('display', 'block');
                    $('#app-jiangli0').text(change['reward']);
                    setTimeout(function () {
                        $('.app-jiangshow').css('display', 'none');
                    }, 30000);
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

            lottery.init('lottery');
            //if (logein) {
            $("#lottery .appjiang-button2").click(function () {
                if (click) {
                    return false;
                } else {
                    click = true;
                }
                redpack({
                    'action': "POINT_AT",
                    'activity': "thanks_given",
                    'level': "5000+"
                }, function (dd) {
                    if (dd['left'] == 0) {
                        $('.appjiang-button').removeClass("appjiang-button2");
                        $('.appjiang-button').addClass("appjiang-button1");
                        $('.appprize-mingdan .appjiang-ri p').html('您没有抽奖机会');
                        if (dd['reward'] == null) {
                            return;
                        }
                    } else {
                        $('.appprize-mingdan .appjiang-ri p span').text(dd['left']);
                    }

                    lottery.speed = 100;

                    roll();


                })
                //return;
            });
            //抽奖2
            var onclick = false;
            $('.app-thanksbu2').on('click', function () {
                if (onclick) {
                    return false;
                } else {
                    onclick = true;
                }
                redpack({
                    'action': "POINT_AT",
                    'activity': "thanks_given",
                    'level': "5000-"
                }, function (data) {
                    if (data['left'] == 0) {
                        $('.app-thanksbu').removeClass("app-thanksbu2");

                        $('.app-thanksbu').addClass("app-thanksbu1");
                        $('.yellow1-main .appjiang-ri p').html('您没有抽奖机会');
                        $('.apphongxi').hide();
                        if (data['reward'] == null) {
                            return;
                        }
                    } else {
                        $('.yellow1-main .appjiang-ri p span').text(data['left']);

                    }
                    if (login) {
                        $('.apphongxi').show();
                        $('#thankgi-thanks2 ').text(data['reward']);

                    }

                    onclick = false;


                    //return false;
                })
            })

            redpack({
                'action': "GET_REWARD_INFO",
                'activity': "thanks_given",
                'level': "5000+"
            }, function (da) {
                if (da['left'] == 0) {
                    $('.appjiang-button').removeClass("appjiang-button2");
                    $('.appjiang-button').addClass("appjiang-button1");
                    $('.appprize-mingdan .appjiang-ri p').html('您没有抽奖机会');
                } else {
                    $('.appprize-mingdan .appjiang-ri p span').text(da['left']);
                }
            });
            function redpack2(d) {

                if (d['left'] == 0) {
                    $('.app-thanksbu').removeClass("app-thanksbu2");
                    $('.app-thanksbu').addClass("app-thanksbu1");
                    $('.yellow1-main .appjiang-ri p').html('您没有抽奖机会');
                } else {
                    $('.yellow1-main .appjiang-ri p span').html(d['left']);
                }
            }

            redpack({
                'action': 'GET_REWARD_INFO',
                'activity': "thanks_given",
                'level': "5000-"
            }, redpack2);
//名单
            var str = '';

            redpack({
                'action': 'GET_REWARD',
                'activity': "thanks_given",
                'level': "5000+"
            }, function (date) {
                for (var k = 0, len2 = date['phone'].length; k < len2; k++) {
                    var tel = date['phone'][k].substring(0, 3) + "******" + date['phone'][k].substring(9, 11);

                    str += '<p>恭喜' + tel + '获得<span>' + date['rewards'][k] + '</span></p>';
                }


                $('.long-p').append(str);
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


            function redpack(data, callback) {
                org.ajax({
                    url: '/api/activity/reward/',
                    type: "POST",
                    data: data,
                    async: false,
                    success: function (data) {
                        change = data;
                        callback && callback(data);


                    }
                })
            }

        })

    },
    other: function () {

    }
})
