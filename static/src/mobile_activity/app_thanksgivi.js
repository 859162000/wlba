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

//抽奖
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
        alert(123);
        click = false;
    } else {
        if (lottery.times < lottery.cycle) {
            lottery.speed -= 10;
        } else if (lottery.times == lottery.cycle) {
            //奖品位置
            //var index = Math.random() * (lottery.count) | 0;
            var index = 6
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
        //console.log(lottery.times + '^^^^^^' + lottery.speed + '^^^^^^^' + lottery.prize);
        lottery.timer = setTimeout(roll, lottery.speed);
    }
    return false;
}

var click = false;

window.onload = function () {
    lottery.init('lottery');
    $("#lottery .appjiang-button").click(function () {
        if (click) {
            return false;
        } else {
            lottery.speed = 100;
            roll();
            click = true;
            //alert(4);
            return false;
        }
    });
};

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
var change = [];
redpack({
    'action': "GET_REWARD_INFO",
    'activity': "thanks_given"
    //'level': "5000+"
}, function () {
    //if (change['left'] == 0) {
    //    $('.jiang-button').removeClass("jiang-button2");
    //    $('.jiang-button').addClass("jiang-button1");
    //    $('.prize-ri p').html('您没有抽奖机会');
    //} else {
    //    $('.app-jihui').text(change['left']);
    //}
});
function redpack(data, callback) {
    org.ajax({
        url: '/api/activity/reward/',
        type: "POST",
        data: data,
        async: false,
        success: function (data) {
            change = data;
            callback && callback(data);
            console.log(change);

            // $('.app-jihui1').text(change['left']);

            //if (change['is_first'] == false) {
            //    $('.kuang-tidhi').addClass("kuang-tidhi12");
            //} else if (change['is_first'] == true) {
            //    $('.kuang-tidhi').removeClass("kuang-tidhi12");
            //}
            //
            //$('#app-jiangli').text(change['reward']);
        }
    })
}