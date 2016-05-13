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

    function goBuy(){
        $(".js-go-buy").on("click",function(){
            var self = $(this),
                url = self.attr("data-src");
            window.location.href = url;
        });
    }

    var login = false;
    wlb.ready({
        app: function (mixins) {
            function connect(data) {
                org.ajax({
                    url: '/accounts/token/login/ajax/',
                    type: 'post',
                    data: {
                        token: data.tk,
                        secret_key: data.secretToken,
                        ts: data.ts
                    },
                    success: function (data) {
                        var url = location.href;
                        var times = url.split("?");
                        if(times[1] != 1){
                            url += "?1";
                            self.location.replace(url);
                        }
                        goBuy();
                    }
                })
            }
            $(".js-go-buy").on("click",function(){
                var self = $(this),
                    url = self.attr("data-src");
                if(login){
                    window.location.href = url;
                }
                mixins.sendUserInfo(function (data) {
                    if (data.ph == '') {
                        login = false;
                        mixins.loginApp({refresh: 1, url: 'https://staging.wanglibao.com/activity/h5_shield_plan/'});
                    } else {
                        login = true;
                        connect(data);
                    }
                });
            });
            mixins.shareData({title: "网利宝金盾计划上线，降低用户投资风险", content: "投资无多少 安全无大小", image: 'https://staging.wanglibao.com/static/imgs/mobile_activity/shield_plan/share.png'});
        },
        other: function(){
            goBuy();
            weixin_share("网利宝金盾计划上线，降低用户投资风险");//微信分享
        }
    });
})(org);
