$(function(){
    var mySwiper = new Swiper ('.swiper-container1', {
      direction: 'vertical',
      loop: false,
      onTouchEnd:function(){
        if(mySwiper.activeIndex == 6){
             $('.page-next').hide()
         }else{
            $('.page-next').show()
        }
      }
   });
    var mySwiper2 = new Swiper ('.swiper-container2', {
      pagination: '.swiper-pagination',
      paginationClickable: true,
      spaceBetween: 30,
      effect:'fade',
      loop: true,
      onTouchEnd: function(swiper){
         console.log(mySwiper2.activeIndex)
         $('.swiper-container2').find('.z-hideToLeft').removeClass('z-hideToLeft');
         $('.swiper-container2').find('.swiper-slide').eq(mySwiper2.previousIndex).css({'z-index':'10000'}).addClass('z-hideToLeft')
         setTimeout(function(){
             $('.swiper-container2').find('.swiper-slide').css({'z-index':'0'})
            $('.swiper-container2').find('.swiper-slide').eq(mySwiper2.activeIndex).css({'z-index':'11000'}).addClass('z-hideToLeft')
         },300)
         //var parent = $('#swiper-container2').find('.swiper-slide')
         //parent.css({'z-index':'0'})
         //parent.find('img').removeClass('translate3d').removeClass('translate3d1')
         //if(mySwiper2.activeIndex > mySwiper2.previousIndex){
         //   parent.eq(mySwiper2.previousIndex).find('img').css({'z-index':'11000'}).addClass('translate3d1')
         //}else{
         //   parent.eq(mySwiper2.previousIndex).find('img').css({'z-index':'11000'}).addClass('translate3d')
         //}
         // parent.eq(mySwiper2.activeIndex).css({'z-index':'10000'})
      }
   });
    //t = $;
    //function e(t, e, n, i) {
     //   return Math.abs(t - e) >= Math.abs(n - i) ? t - e > 0 ? "Left": "Right": n - i > 0 ? "Up": "Down"
    //}
    //function n() {
     //   u = null,
     //   h.last && (h.el.trigger("longTap"), h = {})
    //}
    //function i() {
     //   u && clearTimeout(u),
     //   u = null
    //}
    //function a() {
     //   s && clearTimeout(s),
     //   l && clearTimeout(l),
     //   c && clearTimeout(c),
     //   u && clearTimeout(u),
     //   s = l = c = u = null,
     //   h = {}
    //}
    //function o(t) {
     //   return ("touch" == t.pointerType || t.pointerType == t.MSPOINTER_TYPE_TOUCH) && t.isPrimary
    //}
    //function r(t, e) {
     //   return t.type == "pointer" + e || t.type.toLowerCase() == "mspointer" + e
    //}
    //var s, l, c, u, d, h = {},
    //f = 750;
    //t(document).ready(function() {
     //   var p, g, m, v, x = 0,
     //   b = 0;
     //   "MSGesture" in window && (d = new MSGesture, d.target = document.body),
     //   t(document).bind("MSGestureEnd",
     //   function(t) {
     //       var e = t.velocityX > 1 ? "Right": -1 > t.velocityX ? "Left": t.velocityY > 1 ? "Down": -1 > t.velocityY ? "Up": null;
     //       e && (h.el.trigger("swipe"), h.el.trigger("swipe" + e))
     //   }).on("touchstart MSPointerDown pointerdown",
     //   function(e) { (!(v = r(e, "down")) || o(e)) && (m = v ? e: e.touches[0], e.touches && 1 === e.touches.length && h.x2 && (h.x2 = void 0, h.y2 = void 0), p = Date.now(), g = p - (h.last || p), h.el = t("tagName" in m.target ? m.target: m.target.parentNode), s && clearTimeout(s), h.x1 = m.pageX, h.y1 = m.pageY, g > 0 && 250 >= g && (h.isDoubleTap = !0), h.last = p, u = setTimeout(n, f), d && v && d.addPointer(e.pointerId))
     //   }).on("touchmove MSPointerMove pointermove",
     //   function(t) { (!(v = r(t, "move")) || o(t)) && (m = v ? t: t.touches[0], i(), h.x2 = m.pageX, h.y2 = m.pageY, x += Math.abs(h.x1 - h.x2), b += Math.abs(h.y1 - h.y2))
     //   }).on("touchend MSPointerUp pointerup",
     //   function(n) { (!(v = r(n, "up")) || o(n)) && (i(), h.x2 && Math.abs(h.x1 - h.x2) > 30 || h.y2 && Math.abs(h.y1 - h.y2) > 30 ? c = setTimeout(function() {
     //           h.el.trigger("swipe"),
     //           h.el.trigger("swipe" + e(h.x1, h.x2, h.y1, h.y2)),
     //           h = {}
     //       },
     //       0) : "last" in h && (30 > x && 30 > b ? l = setTimeout(function() {
     //           var e = t.Event("tap");
     //           e.cancelTouch = a,
     //           h.el.trigger(e),
     //           h.isDoubleTap ? (h.el && h.el.trigger("doubleTap"), h = {}) : s = setTimeout(function() {
     //               s = null,
     //               h.el && h.el.trigger("singleTap"),
     //               h = {}
     //           },
     //           250)
     //       },
     //       0) : h = {}), x = b = 0)
     //   }).on("touchcancel MSPointerCancel pointercancel", a),
     //   t(window).on("scroll", a)
    //}),
    //["swipe", "swipeLeft", "swipeRight", "swipeUp", "swipeDown", "doubleTap", "tap", "singleTap", "longTap"].forEach(function(e) {
     //   t.fn[e] = function(t) {
     //       return this.on(e, t)
     //   }
    //})
    //
    //var index = 0;
	//var CascadingTeletext = function($item) {
     //   event.stopPropagation();
     //   event.preventDefault();
	//	var theClass = this;
	//	this.$target = $item.addClass("m-cascadingTeletext"), this.$_currentItem = this.$target.find("li").first().addClass("z-current"), $(window).on("resize", function() {
	//		theClass.$target.height('183px')
	//	}).trigger("resize"), this.$target.find(".imgText").each(function(i, item) {
	//		0 == $.trim(item.innerText).length && $(item).remove()
	//	}), this.$target.on("swipeLeft swipeRight", function(e) {
	//		theClass.$_currentItem.addClass("swipeLeft" == e.type ? "z-hideToLeft" : "z-hideToRight");
     //       if(e.type=='swipeLeft') {
     //           index++;
     //           if(index == 6){
     //               index = 0;
     //               $('.dot-box').find('.active').removeClass('active');
     //               $('.dot-box').find('span').first().addClass('active');
     //           }else{
     //               $('.dot-box').find('.active').removeClass('active').next().addClass('active')
     //           }
     //       }else{
     //           index--;
     //           console.log(index)
     //           if((index == -1) || (index == 0)) {
     //               index = 6;
     //               $('.dot-box').find('.active').removeClass('active');
     //               $('.dot-box').find('span').last().addClass('active');
     //           }else{
     //               $('.dot-box').find('.active').removeClass('active').prev().addClass('active');
     //           }
     //       }
	//	}).delegate("li", "webkitAnimationEnd", function() {
	//		theClass.$target.append(theClass.$_currentItem), theClass.$_currentItem.removeClass("z-current z-hideToLeft z-hideToRight"), theClass.$_currentItem = theClass.$target.find("li").first().addClass("z-current")
	//	})
	//};
	//CascadingTeletext.show = function() {
	//	this.$target.addClass("z-show")
	//};
	//$.fn.cascadingTeletext = function(e) {
	//	var command = "init";
	//	switch (command) {
	//		case "init":
	//			this.each(function(i, item) {
	//				var $item = $(item),
	//					pluginObj = new CascadingTeletext($item);
	//				$item.data("plugin_cascadingTeletext", pluginObj);
	//				//console.log($item.data("plugin_cascadingTeletext", pluginObj));
	//			});
	//			break;
	//		case "getPluginObject":
     //           event.stopPropagation();
     //           event.preventDefault();
	//			return $item.data("plugin_cascadingTeletext")
	//	}
	//	return this;
	//}
    //
	//var $cascadingTeletext = $(".m-cascadingTeletext").cascadingTeletext();


    window.onload = function() {
        window.setTimeout(function(){
            $(".page-loading").hide();
            $("#swiper-container1,.page-common").show()
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