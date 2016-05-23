
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
			shareName = '网利宝携手中影票务通送福利',
			shareImg = host + '/static/imgs/mobile_activity/app_center_film_ticket/300x300.jpg',
			shareLink = host + '/activity/app_center_film_ticket/?promo_token=zypwt',
			shareMainTit = '网利宝携手中影票务通送福利',
			shareBody = '票房最强档 网利宝请您看';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '网利宝携手中影票务通送福利',
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
            mixins.shareData({title: '网利宝携手中影票务通送福利', content: '票房最强档 网利宝请您看'});
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

                        $('#get_ticket').click(function() {
                            org.ajax({
                                url: '/api/activity/zhongying/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1000'){
                                        mixins.registerApp({refresh:1, url:'/activity/app_center_film_ticket/?promo_token=zypwt'});
                                    }else if(data.ret_code=='1001'||data.ret_code=='1002'){
                                        $('.popup_box .main .textairport').text(''+data.message+'');
                                        $('.popup_box').show();
                                    }else if(data.ret_code=='1002'||data.ret_code=='1004'){
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


                    $('#get_ticket').click(function() {
                        mixins.registerApp({refresh:1, url:'/activity/app_center_film_ticket/?promo_token=zypwt'});
                    });
                } else {
                    login = true;
                    connect(data)

                }
            })

        },
        other: function(){
            $('#get_ticket').click(function() {
                org.ajax({
                    url: '/api/activity/zhongying/',
                    type: 'post',
                    success: function (data) {
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=zypwt&next=/activity/app_center_film_ticket/?promo_token=zypwt'
                        }else if(data.ret_code=='1001'||data.ret_code=='1002'){
                            $('.popup_box .main .textairport').text(''+data.message+'');
                            $('.popup_box').show();
                        }else if(data.ret_code=='1002'||data.ret_code=='1004'){
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


    $('.section_5_box p span').on('click',function(){
        var ele = $('.section_5_box .slide_text');
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
        if (!ele.hasClass('down')){
            $('.section_5_box p span').addClass('open');
            ele.height(curHeight).animate({height: autoHeight},500,function(){
                ele.addClass('down');

            });
        }else{
            $('.section_5_box p span').removeClass('open');
            ele.height(curHeight).animate({height: 0},500,function(){
                ele.removeClass('down');

            });
        }
    });

    $('.popup_box .popup_button,.popup_box .close_popup').click(function(){
        $('.popup_box').hide();
    });
})(org);
