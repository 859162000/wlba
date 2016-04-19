$(function(){
     var sixlis = document.getElementById("six_lis"),
         audio = document.getElementById("audios"),
         audiobtn = document.getElementById("audio");
     var ss = 1;
     $('#sec').fullpage();
     sixlis.addEventListener("touchstart",function(){
          $(this).next().slideToggle();
      },false)
     audiobtn.addEventListener("click",function(){
          if(ss == 1){
              $(this).addClass("audio_off");
              audio.pause();
              ss = 2;
          }else{
              audio.play();
              $(this).removeClass("audio_off");
              ss = 1;
          }
     },false);

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
			shareName = '网利宝影像投资节送福利喽',
			shareImg = host + '/static/imgs/mobile_activity/app_august_phone/300x300.jpg',
			shareLink = host + 'weixin_activity/app_august_phone/',
			shareMainTit = '网利宝影像投资节送福利喽',
			shareBody = '全民福利 火速领取';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝影像投资节送福利喽',
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
});


