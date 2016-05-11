
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
			shareName = '网利宝携手迅雷会员疯狂福利趴',
			shareImg = host + '/static/imgs/mobile_activity/app_xunlei_welfare/300X300.jpg',
			shareLink = host + '/activity/app_xunlei_welfare/',
			shareMainTit = '网利宝携手迅雷会员疯狂福利趴',
			shareBody = '迅雷会员免费领，速速前往';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝携手迅雷会员疯狂福利趴',
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

    $('.popup_box .popup_button,.close_popup').click(function(){
        $('.popup_box').hide();
    });

	$('.button').on("click",function(){
		org.ajax({
			type: "post",
			url: "/weixin/fetch_xunlei_vipcard/",
			dataType: 'json',
			success: function(data){
				if(data.ret_code!='0'){
				//成功连接接口
					$('.popup_box .main .textairport').text(''+data.message+'');
					$('.popup_box').show();
				}else{
					$('.popup_box .main .textairport').text(''+data.message+'');
					$('.popup_box').show();
				}
			}
		})
	})

})(org);
