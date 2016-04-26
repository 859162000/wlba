(function(){
	var media1 = $("#media1"),
		media2 = $("#media2");

   var mySwiper = new Swiper ('#page-swipe', {
      direction: 'vertical',
      loop: false,
	  onSlideChangeStart: function(){
		videoFun._pause(media1);
		videoFun._pause(media2);
	  },
      onSlideChangeEnd: function(swiper){
          var self = $(".swiper-slide-active");
          var cname = self.attr("class");
          var inx = cname.indexOf("page");
          var nowDom = cname.substr(inx,5);
          if(nowDom == "page6"){
              $("#next-box").hide();
          }else{
              $("#next-box").show();
          }
      }
   });

	var videoFun = {
		_play: function(dom){//dom == video
			dom.show();
			dom[0].play();
		},
		_pause: function(dom){//dom == video
			dom[0].pause();
			this._showBg(dom);
		},
		_showBg: function(dom){//dom == video
			var sUserAgent = navigator.userAgent.toLowerCase();
			var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
			var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
			if(!bIsIphoneOs && !bIsIpad){
				dom.hide();
			}
			dom.siblings(".video-bg").css("display","-webkit-box");
		},
		init: function(){
			media1.siblings(".video-bg").css("background-image","url('"+ media1.attr("poster") +"')");
			media2.siblings(".video-bg").css("background-image","url('"+ media2.attr("poster") +"')");
		}
	};
	videoFun.init();
	$("div.tab-cont .video-btn").on("click",function(){
		var self = $(this),
			tp = self.parents(".video-bg");
		tp.hide();
		videoFun._play(tp.siblings("video"));
	});
	media1[0].addEventListener("ended",function(){//视频结束
		videoFun._showBg(media1);

	});
	media2[0].addEventListener("ended",function(){//视频结束
		videoFun._showBg(media2)
	});
	//tab
	$("div.page6-tab-nav .tab-nav").click(function(){
		var self = $(this),
			inx = $(this).index(),
			cont = self.parents("div.page6-tab-nav").siblings("div.tab-cont").find(".cont-item"),
			contSib = cont.eq(inx).siblings(".cont-item");
		self.addClass("active").siblings(".tab-nav").removeClass("active");
		cont.removeClass("active").eq(inx).addClass("active");
		videoFun._pause(contSib.find("video"));
	});

	var t = window.setTimeout(preLoad, 100);
	var step = 0;
    function preLoad() {
		var percent = $("#load-txt"),
			imgAn = $("div.load-now");
		percent.text(step + "%");
		imgAn.animate({ width: step + "%" }, 10);
        step += 1;
        if (step <= 100) {
            t = window.setTimeout(preLoad, 10);
        } else {
			clearTimeout(t);
			$("#page-loading").hide();
			$("#next-box,#page-swipe").show();
		}
    }

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
            var winHost = window.location.href;
            var host = winHost.substring(0,winHost.indexOf('/activity')),
			//var host = 'https://staging.wanglibao.com',
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = host + '/activity/weixin_lifestyle/',
                shareMainTit = shareTit,
                shareBody = '2015，你的收益如何？让他们来跟你分享下，投资创造美好生活的心得吧~';
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
	weixin_share("网利宝,是一种生活方式");//微信分享

     wlb.ready({
         app: function(mixins){
             //mixins.loginApp()
             ///document.getElementById('refresh').onclick= function(){
             //    window.location.href=window.location.href;
             //}

            mixins.shareData({title: "网利宝,是一种生活方式", content: "2015，你的收益如何？让他们来跟你分享下，投资创造美好生活的心得吧~"})
         }
     })
})();
