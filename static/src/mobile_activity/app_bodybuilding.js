
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
			shareName = '锐客联盟健身会所携手网利宝  0元邀您健身',
			shareImg = host + '/static/imgs/mobile_activity/app_bodybuilding/300x300.jpg',
			shareLink = host + '/activity/app_bodybuilding/?promo_token=ruike',
			shareMainTit = '锐客联盟健身会所携手网利宝  0元邀您健身',
			shareBody = '引爆完美身型新风尚 还不快快来';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '锐客联盟健身会所携手网利宝  0元邀您健身',
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


    var login = false;
    wlb.ready({
        app: function (mixins) {
            mixins.shareData({title: '锐客联盟健身会所携手网利宝  0元邀您健身', content: '引爆完美身型新风尚 还不快快来'});
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
                                url: '/api/activity/ruike/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1000'){
                                        mixins.registerApp({refresh:1, url:'/activity/app_bodybuilding/?promo_token=ruike'});
                                    }else if(data.ret_code=='1001'){
                                        $('.popup_box .main .textairport').text(''+data.message+'');
                                        $('.popup_box').show();
                                        $('.popup_box .popup_button').click(function(){
                                            mixins.jumpToManageMoney();
                                        });

                                    }else if(data.ret_code=='1002'||data.ret_code=='1003'||data.ret_code=='1004'||data.ret_code=='0'){
                                        $('.popup_box .main .textairport').text(''+data.message+'');
                                        $('.popup_box').show();
                                        $('.popup_box .popup_button').click(function(){
                                            $('.popup_box').hide();
                                        });
                                    }else{
                                        $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                                        $('.popup_box').show();
                                        $('.popup_box .popup_button').click(function(){
                                            $('.popup_box').hide();
                                        });
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
                        mixins.registerApp({refresh:1, url:'/activity/app_bodybuilding/?promo_token=ruike'});
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
                    url: '/api/activity/ruike/',
                    type: 'post',
                    success: function (data) {
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=ruike&next=/activity/app_bodybuilding/?promo_token=ruike'
                        }else if(data.ret_code=='1001'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                            $('.popup_box .popup_button').click(function() {
                                window.location.href = '/weixin/list/?promo_token=ruike'
                            });
                        }else if(data.ret_code=='1002'||data.ret_code=='1003'||data.ret_code=='1004'||data.ret_code=='0'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                            $('.popup_box .popup_button').click(function(){
                                $('.popup_box').hide();
                            });
                        }else{
                            $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                            $('.popup_box').show();
                            $('.popup_box .popup_button').click(function(){
                                $('.popup_box').hide();
                            });
                        }
                    }
                })
            })
        }
    })

    $('.slideDown_button').on('click',function(){
        var ele = $('.slideDown_box');
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
        if (!ele.hasClass('down')){
            $('.slideDown_button').addClass('open');
            ele.height(curHeight).animate({height: autoHeight},500,function(){
                ele.addClass('down');

            });
        }else{
            $('.slideDown_button').removeClass('open');

            ele.height(curHeight).animate({height: 0},500,function(){
                ele.removeClass('down');

            });
        }
    });
	//
    $('.popup_box .close_popup').click(function(){
        $('.popup_box').hide();
    });

})(org);
