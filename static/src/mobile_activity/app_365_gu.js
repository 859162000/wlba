(function(org){
    $('.act_rule_button').on('click',function(){
        var ele = $('.act_rule_wrap');
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
        if (!ele.hasClass('down')){
            $('.act_rule_button img').addClass('rotate');
            ele.height(curHeight).animate({height: autoHeight},500,function(){
                ele.addClass('down');
            });
        }else{
            $('.act_rule_button img').removeClass('rotate');
            ele.height(curHeight).animate({height: 0},500,function(){
            	ele.removeClass('down');
            });
        }
    })

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
		var host = 'https://www.wanglibao.com/',
			shareName = '网利宝用户专享福利',
			shareImg = host + '/static/imgs/mobile_activity/app_365_gu/300X300.jpg',
			shareLink = host + '/activity/app_365_gu/',
			shareMainTit = '网利宝用户专享福利',
			shareBody = '网利宝理财券&365谷礼包任性送'
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝用户专享福利',
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

})(org);

