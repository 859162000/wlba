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
			shareName = '网利宝影像投资节送福利喽',
			shareImg = host + '/static/imgs/mobile_activity/app_august_phone/300x300.jpg',
			shareLink = host + 'weixin_activity/app_august_phone/',
			shareMainTit = '网利宝影像投资节送福利喽',
			shareBody = '全民福利 火速领取';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝影像投资节送福利喽',
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

        $('#show_button').on('click',function(){
            var ele = $('#show_list');
            var curHeight = ele.height();
            var autoHeight = ele.css('height', 'auto').height();
            if (!ele.hasClass('down')){
                ele.height(curHeight).animate({height: autoHeight},500,function(){
                    ele.addClass('down');
                });
            }else{
                ele.height(curHeight).animate({height: 0},500,function(){
                    ele.removeClass('down');
                });
            }
        })

        $('.popup_button').click(function(){
            $('.popup_box').hide();
        });



    wlb.ready({
        app: function(mixins) {
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
                        var url = location.href;
                        var times = url.split("?");
                        if(times[1] != 1){
                            url += "?1";
                            self.location.replace(url);
                        }
                    }
                })
            }
			mixins.shareData({title: '网利宝影像投资节送福利喽', content: '全民福利 火速领取'});
            mixins.sendUserInfo(function(data) {
                $('#button_link').click(function() {
                    mixins.jumpToManageMoney();
                });

            })
        },
        other: function() {

            $('#button_link').click(function() {

                window.location.href = '/weixin/list/'

            })
            //console.log('其他场景的业务逻辑');


        }
    });

})(org);
