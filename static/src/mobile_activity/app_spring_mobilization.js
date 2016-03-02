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
            $('.code_wrap').hide();
            $('#take').click(function() {
                window.location.href = '/activity/experience/redirect/'
                //体验金
            });

            $('#take_red').click(function() {
                mixins.jumpToManageMoney();
            });
            mixins.sendUserInfo(function(data) {
                if (data.ph == '') {
                    login = false;
                    $('#register').click(function() {
                       window.location.href = '/activity/experience/redirect/'
                    });
                    $('#go_user').on('click',
                    function() {
                        mixins.loginApp();
                    })
                } else {
                    login = true;
                    $('#register').click(function() {
                        mixins.jumpToManageMoney();
                    });
                    $('#go_user').on('click',
                    function() {
                        mixins.jumpToManageMoney();
                    })
                }
            })
        },
        other: function() {
            $('.code_wrap').show();

            $('#take').click(function() {
                window.location.href = '/activity/experience/mobile/';
                //体验金
            });

            $('#register').click(function() {
				window.location.href = '/activity/experience/mobile/';
            });
            $('#go_user').on('click',
            function() {
                window.location.href = '/activity/app_gold_season/';
            });
            $('#take_red').on('click',
            function() {
                if (h5_user_static) {
                    window.location.href = '/weixin/list/'
                } else {
                    window.location.href = '/weixin/regist/?next=/weixin/list/'
                }
            });
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
			shareImg = host + '/static/imgs/mobile_activity/app_noviceDecember_h5/300x300.jpg',
			shareLink = host + '/activity/app_noviceDecember_h5/',
			shareMainTit = '网利宝用户专享福利',
			shareBody = '网利宝送你新手福利大红包，快来领哦！';
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

    $('.card_box').click(function(){
        $(this).find('.card').addClass('card_box_open');
    })
})(org);
