(function(org) {
    var h5_user_static;
    org.ajax({
        url: '/api/user_login/',
        type: 'post',
        success: function(data1) {
            h5_user_static = data1.login;
            if(h5_user_static){
                    $('span#zero').hide();
                    $('span#chance_num').css('display','inline-block');
                }else {
                $('span#chance_num').hide();
                $('span#zero').css('display', 'inline-block');

            }
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
            $('.button').click(function() {
                if (h5_user_static) {
                    window.location.href = '/weixin/list/'
                } else {
                    window.location.href = '/weixin/login/?next=/weixin/list/'
                }
            })
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

        var time_count2 = 3;
        /*倒数秒数*/
        var time_intervalId2;
        /*定义倒计时的名字*/

        var timerFunction2 = function () {
        /*定义倒计时内容*/
            if (time_count2 > 1) {
                time_count2--;
                return
            } else {
                clearInterval(time_intervalId2);
                /*清除倒计时*/
                $('.popup_box').show();
                /*解锁按钮，可以点击*/
            }
        };

        /*翻牌*/
        var chance_num;
        var card_no;
        $('.card_box').click(function(){
            card_no=$(this).attr('data-card');
            if(h5_user_static){
                chance_num = $('#chance_num').text();
                if(chance_num>0){
                    if(!$(this).find('.card').hasClass('card_box_open')){
                        chance_num--;
                        $('#chance_num').text(chance_num);
                        luck_draw();
                        //$('.card_box[data-card="'+card_no+'"] .num').text('qwe');
                        //$(this).find('.card').addClass('card_box_open');
                    }

                }else{
                    $('.popup_box .text').text('您还没有翻牌机会，赶紧去投资吧');
                    $('.popup_box').show();
                    time_count = 3;
                    time_intervalId = setInterval(timerFunction, 1000);
                    time_intervalId;
                }



            }else{
                window.location.href = '/weixin/login/?next=/weixin_activity/spring_reward/'
            }

        });

        $('.popup_button').click(function(){
            $('.popup_box').hide();
            $('.popup_box .popup_button').hide();
            $('.card').removeClass('card_box_open');
        });
        /*翻牌结束*/


        /*翻牌抽奖*/
        function luck_draw(){
            org.ajax({
                url: '/api/march_reward/fetch/',
                type: 'post',
                success: function (data1) {
                    if(data1.ret_code==0){
                        $('.card_box[data-card="'+card_no+'"] .num').text(data1.redpack.amount+'元');
                        $('.card_box[data-card="'+card_no+'"]').find('.card').addClass('card_box_open');

                        $('.popup_box .text').text('"恭喜您获得"+data1.redpack.amount+"元红包"');
                        $('.popup_box .popup_button').show();
                        $('.popup_box').show();

                        time_count2 = 3;
                        time_intervalId2 = setInterval(timerFunction2, 1000);
                        time_intervalId2;
                    }else{
                        $('.popup_box .text').text(data1.message);
                        $('.popup_box').show();
                        time_count = 3;
                        time_intervalId = setInterval(timerFunction, 1000);
                        time_intervalId;
                    }


                },error: function(data1){
                    $('.popup_box .text').text(data1.message);
                    $('.popup_box').show();
                    time_count = 3;
                    time_intervalId = setInterval(timerFunction, 1000);
                    time_intervalId;
                }
            })
        }
        /*翻牌抽奖结束*/

})(org);
