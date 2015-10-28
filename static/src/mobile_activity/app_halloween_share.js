/**
 * Created by wxq on 15-10-27.
 */
(function(){
    //微信分享
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ'];
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

        var host = 'https://staging.wanglibao.com/',
            shareName = '万圣夜出门的结果就是......',
            shareImg = host + '/static/imgs/mobile_activity/app_halloween/weixin.jpg',
            shareLink = host + '/activity/app_halloween/',
            shareMainTit = '万圣夜出门的结果就是......',
            shareBody = '没事别瞎溜达，除非......'
        //分享给微信好友
        org.onMenuShareAppMessage({
            title: shareMainTit,
            desc: shareBody,
            link: shareLink,
            imgUrl: shareImg
        });
        //分享给微信朋友圈
        org.onMenuShareTimeline({
            title: '万圣夜出门的结果就是......',
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