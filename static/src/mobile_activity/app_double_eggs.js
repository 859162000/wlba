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
			//mixins.shareData({title: '双旦来了，翻倍狂欢', content: '红包、加息券、体验金全部翻倍送、实物大奖同台登场，年底倾囊N重回馈。'});
			mixins.registerHandler('shareData', function(data, responseCallback) {
                  var app_share_text = { title:'双旦来了，翻倍狂欢', content: '红包、加息券、体验金全部翻倍送、实物大奖同台登场，年底倾囊N重回馈。' };
                  responseCallback(app_share_text);
			});
            mixins.sendUserInfo(function(data) {
				$('.link_licai').click(function(){
					mixins.jumpToManageMoney();
				});
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
				$('#tiyanjin').click(function(){
					window.location.href = '/activity/experience/redirect/'
				});
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
			$('.link_licai').click(function(){
				window.location.href = '/weixin/list/'
			});
			$('#tiyanjin').click(function(){
				window.location.href = '/activity/experience/mobile/';
			});
			$('.code_wrap').show();
            //console.log('其他场景的业务逻辑');
        }
    });

	var see_rule_button_index;
	$('.see_rule_button').click(function(){
		see_rule_button_index = $(this).next().hasClass('rule_wrap_show');
		if(see_rule_button_index){
			$(this).next().removeClass('rule_wrap_show').hide();
		}else{
			$(this).next().addClass('rule_wrap_show').show();
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
			shareName = '双旦来了，翻倍狂欢',
			shareImg = host + '/static/imgs/mobile_activity/app_double_dan/300x300.jpg',
			shareLink = host + '/activity/app_double_dan/',
			shareMainTit = '双旦来了，翻倍狂欢',
			shareBody = '红包、加息券、体验金全部翻倍送、实物大奖同台登场，年底倾囊N重回馈。';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '双旦来了，翻倍狂欢',
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


