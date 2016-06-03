
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
			shareName = '网利宝免费萌娃礼 只为爱升温！',
			shareImg = host + '/static/imgs/mobile_activity/app_baby_box/300*300.jpg',
			shareLink = host + '/activity/app_baby_box/?promo_token=bg',
			shareMainTit = '网利宝免费萌娃礼 只为爱升温！',
			shareBody = '最好的爱 只为予你';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝免费萌娃礼 只为爱升温！',
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

	wlb.ready({
        app: function (mixins) {
            mixins.shareData({title: '网利宝免费萌娃礼 只为爱升温！', content: '网利宝免费萌娃礼 只为爱升温！'});
            function connect(data) {
                org.ajax({
                    url: '/accounts/token/login/ajax/',
                    type: 'post',
                    data: {
                        token: data.tk,
                        secret_key: data.secretToken,
                        ts: data.ts
                    },
                    success: function (data) {

                        //var url = location.href;
                        //var times = url.split("?");
                        //if(times[1] != 1){
                        //    url += "?1";
                        //    self.location.replace(url);
                        //}

                        $('#take_prize,#take_prize_2').click(function() {
                            org.ajax({
                                url: '/api/activity/baobeigezi/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1000'){
                                        mixins.registerApp({refresh:1, url:'/activity/app_baby_box/?promo_token=bg'});
                                    }else if(data.ret_code=='1002'){
                                        mixins.jumpToManageMoney();
                                    }else if(data.ret_code=='1001'||data.ret_code=='1002'||data.ret_code=='1004'){
                                        $('.popup_box .main .textairport').text(''+data.message+'');
                                        $('.popup_box').show();
                                    }else{
                                        $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                                        $('.popup_box').show();
                                    }
                                }
                            })
                        })
                    }
                })
            }
            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    login = false;


                    $('#take_prize,#take_prize_2').click(function() {
                        mixins.registerApp({refresh:1, url:'/activity/app_baby_box/?promo_token=bg'});
                    });
                } else {
                    login = true;
                    connect(data)

                }
            })

        },
        other: function(){
            $('#take_prize,#take_prize_2').click(function() {
                org.ajax({
                    url: '/api/activity/baobeigezi/',
                    type: 'post',
                    success: function (data) {
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=bg&next=/activity/app_baby_box/?promo_token=bg'
                        }else if(data.ret_code=='1002'){
                            window.location.href = '/p2p/list/?promo_token=bg'
                        }else if(data.ret_code=='1001'||data.ret_code=='1002'||data.ret_code=='1004'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                        }else{
                            $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                            $('.popup_box').show();
                        }
                    }
                })
            })
        }
    })

    $('.popup_box .popup_button,.popup_box .close_popup').click(function(){
        $('.popup_box').hide();
    });
})(org);
