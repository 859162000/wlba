
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
			shareLink = host + '/activity/app_baby_box/h5/?promo_token=bg',
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
			title: '网利宝免费萌娃礼 只为爱升温！”',
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

    $('#take_prize,#take_prize_2').click(function() {
        org.ajax({
            url: '/api/activity/baobeigezi/',
            type: 'post',
            success: function (data) {
                if(data.ret_code=='1000'){
                    window.location.href = '/weixin/regist/?promo_token=bg&next=/activity/app_baby_box/h5/?promo_token=bg'
                }else if(data.ret_code=='1002'){
                    window.location.href = '/weixin/list/?promo_token=bg'
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



    $('.popup_box .popup_button,.popup_box .close_popup').click(function(){
        $('.popup_box').hide();
    });
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
})(org);
