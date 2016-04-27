$(function(){
    var mySwiper = new Swiper ('#swiper-container', {
      direction: 'vertical',
      loop: false,
      onSlideChangeStart:function(swiper){
        if(mySwiper.activeIndex == 3){
            $('#next-box').hide();
            //mySwiper.destroy(false, true);
        }else{
            $('#next-box').show();
        }
      }
    });

    window.onload = function() {
        window.setTimeout(function(){
            $(".page-loading").hide();
            $("#swiper-container .swiper-wrapper,#next-box").show();
        }, 1000);
    };

    //音乐
    var audioBox = document.getElementById("js-audio"),
        audioDom = audioBox.getElementsByTagName("audio")[0];
    $(audioBox).on("touchstart", function(){
        var $t = $(this);
        if(audioDom.paused){
            audioDom.play();
            $t.removeClass("audio-close");
        }else{
            audioDom.pause();
            $t.addClass("audio-close");
        }
    });

    $("div.swiper-container").one("touchstart",function(){
        if(audioDom.paused){
            audioDom.play();
        }
    });

    //弹层
    $("div.js-close").on("touchstart", function(){
        $(this).parents(".page-alt").hide();
    });
    //规则
    $("div.js-rule").on("touchstart", function(){
        $("div.alt-rule").css("display","-webkit-box");
    });
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
        var winHost = window.location.href;
        var host = winHost.substring(0,winHost.indexOf('/activity')),
            shareImg = host + '/static/imgs/mobile_activity/new_user_gift/icon_weixin.png',
            shareLink = host + '/weixin/new_user_gift/',
            shareMainTit = '尊贵新人礼 专享5%加息',
            shareBody = '网利宝新手狂撒福利';
        //分享给微信好友
         org.onMenuShareAppMessage({
            title: shareMainTit,
            desc: shareBody,
            link: shareLink,
            imgUrl: shareImg
        });
        //分享给微信朋友圈
        org.onMenuShareTimeline({
            title: shareMainTit,
            link : shareLink,
            imgUrl: shareImg
        });
        //分享给QQ
        org.onMenuShareQQ({
            title: shareMainTit,
            desc: shareBody,
            link : shareLink,
            imgUrl: shareImg
        });
    });

    function get_gift(){
        //领取加息券
        $("button.js-receive").on("touchstart", function(){
            var $ok = $("div.alt-ok"),
                $tit = $ok.find("div.alt-tit");
            var self = $(this);
            self.attr("disabled", true).text("正在提交……");
            org.ajax({
                type: "post",
                url: "/api/activity/newusergift/",
                dataType: 'json',
                success: function(data){
                    if(data.ret_code === 0){
                        $ok.css("display","-webkit-box");
                        $tit.html('领取加息特权成功～<br />请前往[账户]-[理财券]中查看');
                    }else if(data.ret_code === 1){
                        $ok.css("display","-webkit-box");
                        $tit.html(data.message);
                    }else{
                        $("div.alt-error").css("display","-webkit-box").find(".alt-tit").html(data.message);
                    }
                },
                error: function(xml){
                    if(xml.status === 403){
                        alert("您还没有登录，请先登录");
                    }else{
                        alert("系统繁忙，请稍候再试");
                    }
                },
                complete: function () {
                    self.removeAttr("disabled").text("领取加息特权");
                }
            });
        });
    }

    wlb.ready({
        app: function(mixins){
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
                        get_gift();
                    }
                })
            }
            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    login = false;
                    mixins.loginApp({refresh:1, url:''});
                } else {
                    login = true;
                    connect(data);
                }
            });
            //document.getElementById('refresh').onclick= function(){
            //    window.location.reload();
            //}
            mixins.shareData({title: "尊贵新人礼 专享5%加息", content: "网利宝新手狂撒福利"});
        },
        other: function(){
            get_gift();
        }
    })
});