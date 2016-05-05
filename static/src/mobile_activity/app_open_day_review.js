(function(org) {

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
		var host = location.protocol+"//"+location.host,
			shareName = '春日总动员',
			shareImg = host + '/static/imgs/mobile_activity/app_open_day_review/300x300.png',
			shareLink = host + '/activity/app_open_day_review/',
			shareMainTit = '春日总动员',
			shareBody = '万份豪礼倾情送，全民来抢乐出游！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '春日总动员',
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

    var swiper = new Swiper('.swiper1', {
		pagination : '.pagination1',
		loop:true,
		grabCursor: true
	});
    var swiper_2 = new Swiper('.swiper2', {
		pagination : '.pagination2',
		loop:true,
		grabCursor: true
	});
    var swiper_3 = new Swiper('.swiper3', {
		pagination : '.pagination3',
		loop:true,
		grabCursor: true
	});

})(org);
