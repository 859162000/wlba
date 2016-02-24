
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
//        shareMainTit = '送你28888元体验金+1年迅雷会员',
//        shareBody = '注册即送28888元体验金，首次充值送7天迅雷白金会员，首次投资不低于1000元送1年迅雷白金会员。'
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

})
