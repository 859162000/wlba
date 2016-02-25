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

//微信分享
//var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ',];
//org.ajax({
//    type: 'GET',
//    url: '/weixin/api/jsapi_config/',
//    dataType: 'json',
//    success: function (data) {
//        //请求成功，通过config注入配置信息,
//        wx.config({
//            debug: false,
//            appId: data.appId,
//            timestamp: data.timestamp,
//            nonceStr: data.nonceStr,
//            signature: data.signature,
//            jsApiList: jsApiList
//        });
//    }
//});


//wx.ready(function () {
//
//    var host = 'https://www.wanglibao.com',
//        shareImg = host + '/static/imgs/mobile/share_logo.png',
//        shareLink = host + '/activity/app_xunlei/?promo_token=' + tokenq + '&xluserid=' + xidq + '&time=' + timerq + '&sign=' + sigq + '&nickname=' + nameq + '&referfrom=' + referq,
//        shareMainTit = '送你28888元体验金，体验金专享1天10%年化收益',
//        shareBody = '注册即送28888元体验金，首次充值不低于100元即可获7天迅雷会员及50元直抵红包，首次投资即可获得100元直抵红包,单笔首次投资不低于1000元附加获赠1年迅雷会员。'
//    //分享给微信好友
//    org.onMenuShareAppMessage({
//        title: shareMainTit,
//        desc: shareBody,
//        link: shareLink,
//        imgUrl: shareImg
//    });
//    //分享给微信朋友圈
//    org.onMenuShareTimeline({
//        title: shareMainTit,
//        link: shareLink,
//        imgUrl: shareImg
//    })
//    //分享给QQ
//    org.onMenuShareQQ({
//        title: shareMainTit,
//        desc: shareBody,
//        link: shareLink,
//        imgUrl: shareImg
//    })
//})


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
            console.log(data);
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