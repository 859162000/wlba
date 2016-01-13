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
			mixins.shareData({title: '2016年1月年终奖', content: '终于成功领到了1月年终奖，感谢老板！'});

            mixins.sendUserInfo(function(data) {
				if (data.ph == '') {
                    $('#go_experience').click(function() {
					   mixins.loginApp({refresh:1, url:'https://staging.wanglibao.com/activity/experience/account/'});
					})
                } else {
                    $('#go_experience').click(function() {
						window.location.href = '/activity/experience/account/';
					})
                }

				$('.button').click(function(){
					mixins.jumpToManageMoney();
				});
            });
        },
        other: function() {
			$('.button').click(function(){
				window.location.href = '/weixin/list/';
			});

			$('#go_experience').click(function() {
				window.location.href = '/activity/experience/account/';
			})

        }
    });


	$('#see_rule_1').on('click',function(){
		var ele = $('.rule_wrap_1');
		var curHeight = ele.height();
		var autoHeight = ele.css('height', 'auto').height();
		if (!ele.hasClass('down')){
			$('#see_rule_1').addClass('select');
			ele.height(curHeight).animate({'height':autoHeight},500,function(){
				ele.addClass('down');
			});
		}else{
			$('#see_rule_1').removeClass('select');
			ele.height(curHeight).animate({'height':'0'},500,function(){
				ele.removeClass('down');
			});
		}
	})
	$('#see_rule_2').on('click',function(){
		var ele = $('.rule_wrap_2');
		var curHeight = ele.height();
		var autoHeight = ele.css('height', 'auto').height();
		if (!ele.hasClass('down')){
			$('#see_rule_2').addClass('select');
			ele.height(curHeight).animate({'height':autoHeight},500,function(){
				ele.addClass('down');
			});
		}else{
			$('#see_rule_2').removeClass('select');
			ele.height(curHeight).animate({'height':'0'},500,function(){
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
			shareName = '2016年1月年终奖',
			shareImg = host + '/static/imgs/mobile_activity/app_january_reward/300x300.jpg',
			shareLink = host + '/activity/app_january_reward/',
			shareMainTit = '2016年1月年终奖',
			shareBody = '终于成功领到了1月年终奖，感谢老板！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '10倍体验金，还有最高2.8%和3000直抵红包！',
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


