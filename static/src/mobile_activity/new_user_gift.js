$(function(){
    var mySwiper = new Swiper ('#swiper-container', {
      direction: 'vertical',
      loop: false,
      onSlideChangeStart:function(){
        if(mySwiper.activeIndex == 3){
             $('#next-box').hide()
         }else{
            $('#next-box').show()
        }
      }
    });

    window.onload = function() {
        window.setTimeout(function(){
            $(".page-loading").hide();
            $("#swiper-container .swiper-wrapper,#next-box").show();
        }, 1000);
    };

    //弹层
    $("div.js-close").on("touchstart", function(){
        $(this).parents(".page-alt").hide();
    });
    //规则
    $("div.js-rule").on("touchstart", function(){
        $("div.alt-rule").css("display","-webkit-box");
    });

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

    //音乐
    var audioBox = document.getElementById("js-audio"),
        audioDom = audioBox.getElementsByTagName("audio")[0];
    $(audioBox).on("touchstart", function(){
        var $t = $(this);
        console.log(audioDom.paused);
        if(audioDom.paused){
            audioDom.play();
            $t.removeClass("audio-close");
        }else{
            audioDom.pause();
            $t.addClass("audio-close");
        }
    });


    wlb.ready({
        app: function(mixins){
            mixins.loginApp();
            document.getElementById('refresh').onclick= function(){
                window.location.reload();
            }
            mixins.shareData({title: "网利宝,是一种生活方式", content: "2015，你的收益如何？让他们来跟你分享下，投资创造美好生活的心得吧~"});
        },
        other: function(){
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
                    shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                    shareLink = host + '/activity/h5_recruit/',
                    shareMainTit = '极致工作疯狂玩乐，最有“宝”的互联网金融公司',
                    shareBody = '2016我们一起High，你来不来？';
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
        }
    })
});