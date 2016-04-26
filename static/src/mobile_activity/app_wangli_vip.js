(function(org) {
    var h5_user_static;
    org.ajax({
        url: '/api/user_login/',
        type: 'post',
        success: function(data1) {
            h5_user_static = data1.login;
        }
    });
    var login = false;

    $('.banner_main .view').on('click',function(){
        var ele = $('#banenr .slide_bottom');
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
		$('.banner_main .view').addClass('view_activate');
		ele.height(curHeight).animate({height: autoHeight},500);

    });

	$('#banenr .slide_bottom .bottom_arrow').click(function(){
		var ele = $('#banenr .slide_bottom');
        var curHeight = ele.height();
		$('.banner_main .view').removeClass('view_activate');
		ele.height(curHeight).animate({height: 0},500);
	});



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
			shareName = '网利宝会员初体验',
			shareImg = host + '/static/imgs/mobile_activity/app_wangli_vip/300x300.jpg',
			shareLink = host + 'activity/app_wangli_vip/',
			shareMainTit = '网利宝会员初体验',
			shareBody = '多种特权接入中，总有一款适合你！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝会员初体验',
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
