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
                if (data.ph == '') {
                    login = false;

                    $('.button').click(function() {
                        mixins.loginApp();
                    });

                } else {
                    login = true;
                    $('.button').click(function() {
                        mixins.jumpToManageMoney();
                    });
                }
            })
        },
        other: function() {
            if(h5_user_static){
                window.location.href = '/p2p/list/'
            }else{
                window.location.href = '/accounts/login/?next=/p2p/list/'
            }
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
		var host = 'https://staging.wanglibao.com/',
			shareName = '春日总动员',
			shareImg = host + '/static/imgs/mobile_activity/app_spring_mobilization/300x300.jpg',
			shareLink = host + 'march_reward/app/',
			shareMainTit = '春日总动员',
			shareBody = '万份豪礼倾情送，全民来抢乐出游！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '春日总动员',
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

    var time_count = 3;
        /*倒数秒数*/
        var time_intervalId;
        /*定义倒计时的名字*/

        var timerFunction = function () {
        /*定义倒计时内容*/
            if (time_count > 1) {
                time_count--;
                return $('.popup_box').show();
            } else {
                clearInterval(time_intervalId);
                /*清除倒计时*/
                $('.popup_box').hide();
                /*解锁按钮，可以点击*/
            }
        };

        /*翻牌*/
        $('.card_box').click(function(){
            if(h5_user_static){
                $(this).find('.card_box_main').addClass('card_box_open');
                $('.popup_box').show();


                time_count = 3;
                time_intervalId = setInterval(timerFunction, 1000);
                time_intervalId;


            }else{
                window.location.href = '/accounts/login/?next=/weixin_activity/march_reward/'
            }

        });
        /*翻牌结束*/


        /*翻牌抽奖*/
        $.ajax({
            url: '/api/march_reward/fetch/',
            type: 'post',
            success: function (data1) {

            },error: function(data1){

            }
        })
        /*翻牌抽奖结束*/


})(org);
