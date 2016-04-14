function getQueryString(name) {
    var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return unescape(r[2]);
    }
    return null;
}
var tokenq = getQueryString('promo_token'),
    xidq = getQueryString('xluserid'),
    timerq = getQueryString('time'),
    sigq = getQueryString('sign'),
    nameq = getQueryString('nickname'),
    referq = getQueryString('referfrom');
$('.xunleibutton0,.xunleibutton1,.xunleibutton2,.xunleibutton3').click(function () {

    window.location.href = '/activity/app_xunleizhuce/?promo_token=' + tokenq + '&xluserid=' + xidq + '&time=' + timerq + '&sign=' + sigq + '&nickname=' + nameq + '&referfrom=' + referq

});
$('.signxun1').click(function () {
    window.location.href = '/weixin/login/?promo_token=' + tokenq + '&xluserid=' + xidq + '&time=' + timerq + '&sign=' + sigq + '&nickname=' + nameq + '&referfrom=' + referq + '&next=/activity/app_xunleithree/'
})

org.ajax({
    url: '/api/coop_pv/' + tokenq + '/?source=pv_wanglibao&ext=' + tokenq + '&ext2=' + referq,
    type: "GET"
});

//效果
var click = false;
$('#vertical').find('a').click(function () {
    if (click) {
        return false;
    } else {
        click = true;
    }
    var self = $(this),
        img = self.find('.imgg');
    org.ajax({
        url: "/api/activity/reward/",
        type: "POST",
        data: {activity: 'xunlei'},
        async: false,
        success: function (data) {
            //console.log(data);
            chances();
            if (data['ret_code'] == 0) {
                img.animate({'width': 0}, 500, function () {
                    $(this).hide().next().show();
                    $(this).next().animate({'width': '7rem'}, 500, function () {
                        $('#vertical').find('a').removeClass('xun');
                        setTimeout(function () {
                            self.find('.info').animate({'width': 0}, 500, function () {
                                $(this).hide();
                                img.show();
                                img.animate({'width': '7rem'}, 800, function () {
                                    click = false;
                                });
                            });

                        }, 3000);

                    });

                });
            } else if (data['ret_code'] == 1002) {
                click = true;
            } else if (data['ret_code'] == 1000) {
                //$('body,html').animate({scrollTop: 0}, 600);
                //click = false;
            }
            if (data['experience'] == 3588) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei3588.png");
            } else if (data['experience'] == 1588) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei1588.png");
            } else if (data['experience'] == 1888) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei1888.png");
            } else if (data['experience'] == 2588) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei2588.png");
            } else if (data['experience'] == 5888) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei5888.png");
            } else if (data['experience'] == null && data['redpack'] == null) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei4.png");
            } else if (data['redpack'] == 1.5) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei2.png");
            } else if (data['redpack'] == 1.0) {
                $(".info").attr("src", "/static/imgs/mobile_activity/app_xunleithree/app_paixunlei3.png");
            }
        }
    })


})
chances();
function chances() {
    org.ajax({
        url: "/api/activity/reward/?activity=xunlei&action=generate",
        type: "GET",
        async: false,
        success: function (data) {
            console.log(data);
            if (data['ret_code'] == 0) {
                $('.signxun').text(' ' + data['count'] + ' ');
            }

        }
    })


}