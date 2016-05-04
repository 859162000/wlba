
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
		var host = location.protocol+"//"+location.host,
			shareName = '网利宝影像投资节送福利喽',
			shareImg = host + '/static/imgs/mobile_activity/app_august_phone/300x300.jpg',
			shareLink = host + '/activity/app_august_phone/?promo_token=sy',
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

    $('.popup_box .popup_button').click(function(){
        $('.popup_box').hide();
    });


    var login = false;
    wlb.ready({
        app: function (mixins) {
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

                        $('#button_link').on("click",function(){
                            org.ajax({
                                type: "post",
                                url: "/api/activity/zhaoxiangguan/",
                                dataType: 'json',
                                success: function(data){
                                    if(data.ret_code=='1'){
                                        $('.popup_box .main .textairport').text(''+data.message+'');
                                        $('.popup_box').show();
                                    }else if(data.ret_code=='0'){
                                        if(data.tag=='标记成功'){
                                            mixins.jumpToManageMoney();
                                        }else{
                                            $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                                            $('.popup_box').show();
                                        }
                                    }
                                    //console.log(data)
                                }

                            })
                        })
                    }
                })
            }
            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    login = false;

                    $('#button_link').on("click",function(){
                         mixins.loginApp({refresh:1, url:'/activity/app_august_phone/?promo_token=sy'});
                    })
                } else {
                    login = true;
                    connect(data)

                }
            })

        },
        other: function(){
            $('#button_link').on("click",function(){
                org.ajax({
                    type: "post",
                    url: "/api/activity/zhaoxiangguan/",
                    dataType: 'json',
                    success: function(data){
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=sy&next=/activity/app_august_phone/?promo_token=sy'
                        }else if(data.ret_code=='1'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                        }else if(data.ret_code=='0'){
                             if(data.tag=='标记成功'){
                                window.location.href = '/weixin/list/?promo_token=sy'
                            }else{
                                $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                                $('.popup_box').show();
                            }

                        }else if(data.ret_code=='1001'||data.ret_code=='1002'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                        }
                        //console.log(data)
                    }
                })
            })
        }
    })
})(org);
