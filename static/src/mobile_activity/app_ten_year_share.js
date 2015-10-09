(function(){
    //微信分享
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
    org.ajax({
        type : 'GET',
        url : '/weixin/api/jsapi_config/',
        dataType : 'json',
        success : function(data) {
            //请求成功，通过config注入配置信息,
            wx.config({
                debug: false,
                appId: data.appId,
                timestamp: data.timestamp,
                nonceStr: data.nonceStr,
                signature: data.signature,
                jsApiList: jsApiList
            });
        }
    });


    wx.ready(function(){

        var host = 'https://www.wanglibao.com',
            shareName = '遇到十年前的自己',
            shareImg = host + '/static/imgs/mobile_activity/app_ten_year/weixin_img_300.jpg',
            shareLink = host + '/activity/app_ten_year/',
            shareMainTit = '遇到十年前的自己',
            shareBody = '我刚遇到十年前的自己，你也来试试把...'
        //分享给微信好友
        org.onMenuShareAppMessage({
            title: shareMainTit,
            desc: shareBody,
            link: shareLink,
            imgUrl: shareImg
        });
        //分享给微信朋友圈
        org.onMenuShareTimeline({
            title: '我刚遇到十年前的自己，你也来试试把...',
            link : shareLink,
            imgUrl: shareImg
        })
        //分享给QQ
        org.onMenuShareQQ({
            title: shareMainTit,
            desc: shareBody,
            link : shareLink,
            imgUrl: shareImg
        })
    })
})();
