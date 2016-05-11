;(function(org){
    $("a.js-file").on("touchstart", function(){
        $("div.sp-alt").css("display", "-webkit-box");
    });
    $("div.sp-alt").on("touchstart", function(){
        $(this).hide();
    });

    var scrollTop = false;
    function scrollEvent(){
        var top = document.body.scrollTop;
        var lft = $(".circle-icon-lft"),
            rht = $(".circle-icon-rht");
        //var setEvent = null;
        //console.log(top);
        if( top> 2780 && top < 3500){
            scrollTop = true;
            rht.animate({height: "100%"},function(){
                lft.css("display","block").animate({height: "100%"},500);
            },500);
        }else if(top<2300 || top>3500){
            if(scrollTop){
                scrollTop = false;
                //clearTimeout(setEvent);
                lft.animate({height: 0},function(){
                    lft.css("display","none");
                    rht.animate({height: 0},500);
                },500);
            }
        }
    }
    scrollEvent();
    $("body.h5-shield-plan").on("touchmove", function(){
        scrollEvent();
    });
    function weixin_share(shareTit,fn){
        //alert(shareTit);
        var weiURL = '/weixin/api/jsapi_config/';
        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
        org.ajax({
            type: 'GET',
            url: weiURL,
            dataType: 'json',
            success: function (data) {
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
        wx.ready(function () {
            var winHost = window.location.href,
                host = winHost.substring(0,winHost.indexOf('/activity')) || winHost.substring(0,winHost.indexOf('/weixin'));
            var shareImg = host + '/static/imgs/mobile_activity/shield_plan/share.png',
                shareLink = host + '/activity/weixin_lifestyle/',
                shareMainTit = shareTit,
                shareBody = '投资无多少 安全无大小';
            //分享给微信好友
            org.onMenuShareAppMessage({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert("分享成功");
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给微信朋友圈
            org.onMenuShareTimeline({
                title: shareMainTit,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给QQ
            org.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert(1);
                    if(fn && (typeof fn == "function")){
                        //alert(3);
                        fn();
                    }
                }
            })
        })
    }
	weixin_share("网利宝金盾计划上线，降低用户投资风险");//微信分享
})(org);
