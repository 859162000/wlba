$(function(){
    var mySwiper = new Swiper ('#swiper-container1', {
      direction: 'vertical',
      loop: true
   });
    var mySwiper2 = new Swiper ('#swiper-container2', {
      pagination: '.swiper-pagination',
      paginationClickable: true,
      spaceBetween: 30,
      effect:'fade',
      loop: true,
      onTouchEnd: function(swiper){
         var parent = $('#swiper-container2').find('.swiper-slide')
         parent.css({'z-index':'0'})
         parent.find('img').removeClass('translate3d').removeClass('translate3d1')
         if(mySwiper2.activeIndex > mySwiper2.previousIndex){
            parent.eq(mySwiper2.previousIndex).find('img').css({'z-index':'11000'}).addClass('translate3d1')
         }else{
            parent.eq(mySwiper2.previousIndex).find('img').css({'z-index':'11000'}).addClass('translate3d')
         }
          parent.eq(mySwiper2.activeIndex).css({'z-index':'10000'})
      }
   });
    window.onload = function() {
        window.setTimeout(function(){
            $(".page-loading").hide();
            $("#swiper-container1").show()
        }, 1000);
    }
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
                shareMainTit = '极致工作疯狂玩乐，最有“宝的互联网金融公司”',
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
            })
            //分享给QQ
            org.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link : shareLink,
                imgUrl: shareImg
            })
        })
})