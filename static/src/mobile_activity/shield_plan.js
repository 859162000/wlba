;(function(org){
    $("a.js-file").on("touchstart", function(){
        $("div.sp-alt").css("display", "-webkit-box");
    });
    $("div.sp-alt").on("touchstart", function(){
        $(this).hide();
    });

    //var scrollTop = false;
    //function scrollEvent(){
    //    var top = document.body.scrollTop;
    //    var dom = $(".js-circle-alt");
    //    //var setEvent = null;
    //    var circle_top = $("div.js-circle-box").offset().top,
    //        height = window.innerHeight || document.documentElement.clientHeight,
    //        domH = dom.height();
    //    $(".js-num-box").html(top+" circle_top:"+circle_top+" height:"+height+"<br />circle_top+domH:"+(circle_top+domH-height)+" dom.height:"+dom.height());
    //    //console.log(top >= circle_top && top < (circle_top+domH));
    //    if(top > (circle_top+domH-height) && top < (circle_top+domH+height)){
    //        //alert(top);
    //        scrollTop = true;
    //        dom.addClass("circle-alt-an");
    //    }else if(top<(circle_top-height) || top>(circle_top+domH+height)){
    //        if(scrollTop){
    //            scrollTop = false;
    //            //clearTimeout(setEvent);
    //            dom.removeClass("circle-alt-an");
    //        }
    //    }
    //}
    //scrollEvent();
    //$("body.h5-shield-plan").on("touchmove", function(){
    //    scrollEvent();
    //});
    function weixin_share(shareTit,fn){
        //alert(shareTit);
        var weiURL = '/weixin/api/jsapi_config/';
        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
        var winHost = window.location.href;
        var debug = winHost.split("debug=")[1];
        org.ajax({
            type: 'GET',
            url: weiURL,
            dataType: 'json',
            success: function (data) {
                //请求成功，通过config注入配置信息,
                wx.config({
                    debug: debug,
                    appId: data.appId,
                    timestamp: data.timestamp,
                    nonceStr: data.nonceStr,
                    signature: data.signature,
                    jsApiList: jsApiList
                });
            }
        });
        wx.ready(function () {
            var host = winHost.substring(0,winHost.indexOf('/activity')) || winHost.substring(0,winHost.indexOf('/weixin'));
            var shareImg = host + '/static/imgs/mobile_activity/shield_plan/share.png',
                shareLink = host + '/activity/h5_shield_plan/',
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

    wlb.ready({
        app: function (mixins) {
            mixins.shareData({title: "网利宝金盾计划上线，降低用户投资风险", content: "投资无多少 安全无大小"});
        },
        other: function(){
            weixin_share("网利宝金盾计划上线，降低用户投资风险");//微信分享
        }
    });
})(org);
