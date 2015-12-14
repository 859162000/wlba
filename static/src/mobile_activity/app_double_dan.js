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
    wlb.ready({
        app: function(mixins) {
            mixins.sendUserInfo(function(data) {

				$('.investment_button').click(function() {
					mixins.jumpToManageMoney();
				});

                if (data.ph == '') {
                    login = false;
					$('.recharge_button').click(function() {
                        mixins.loginApp();
                    })
                } else {
                    login = true;
                    $('.recharge_button').click(function() {
                        mixins.jumpToManageMoney();
                    })
                }

            });
			$('.code_wrap').hide();
        },
        other: function() {
            if(h5_user_static){
                $('.recharge_button').click(function() {
                    window.location.href = '/weixin/recharge/?rechargeNext=/weixin/account/'
                })
            }else{
                $('.recharge_button').click(function() {
                    window.location.href = '/weixin/login/?next=/weixin/recharge/'
                })
            }
			$('.investment_button').click(function() {
				window.location.href = '/weixin/list/'
			});
			$('.code_wrap').show();
            //console.log('其他场景的业务逻辑');
        }
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
			shareName = '网利宝用户专享福利',
			shareImg = host + '/static/imgs/mobile_activity/app_recharge_8000/300x300.jpg',
			shareLink = host + '/activity/app_recharge_8000/',
			shareMainTit = '网利宝用户专享福利',
			shareBody = '网利宝双旦来了，翻倍狂欢。跨年最强福利场！';
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
