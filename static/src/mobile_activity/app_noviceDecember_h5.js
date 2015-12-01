(function() {
		$('.take_red').click(function(){
			if($('#denglu').index()){
				$('.title_wrap').show();
			}else{
				window.location.href = '/p2p/list/'
			}
		});

		$('.take_first_red').click(function(){
			if($('#denglu').index()){
				$('.title_wrap').show();
			}else{
				window.location.href = '/accounts/login/?next=/p2p/list/'
			}
		});

		$('.click_rule').click(function(){
			$('.strategy_wrap').addClass('strategy_wrap_show');
		});
		$('.see_red_rule').click(function(){
			$('.recommend_send_red').addClass('recommend_send_red_show');
		});
		$('.title_wrap .close,.title_wrap .button').click(function(){
			$('.title_wrap').hide();
		});

		var login = false;
		//$('.appjiang-button').html(123)
		wlb.ready({
			app: function (mixins) {
				$('#take').click(function () {
					mixins.registerApp();
				});
				$('#take_red').click(function () {
					mixins.jumpToManageMoney();
				});
				mixins.sendUserInfo(function (data) {
					if (data.ph == '') {
						login = false;
						$('#register').click(function(){
							mixins.loginApp();
						})
					} else {
						login = true;
						$('#register').click(function(){
							mixins.jumpToManageMoney();
						})
					}
				})
			},
			other: function(){

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
						shareBody = '网利宝新人大礼包'
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

				$('#register').click(function(){
					window.location.href = '/weixin/regist/'
				});
				$('#take').click(function(){
					$('#title_wrap'){
						/api/user-login
					}
				});
			   	console.log('其他场景的业务逻辑');
			}
		})
	})



