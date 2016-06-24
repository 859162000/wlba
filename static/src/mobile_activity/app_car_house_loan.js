
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
			shareName = '“车房贷”福利专享大放送',
			shareImg = host + '/static/imgs/mobile/weChat_logo.png',
			shareLink = host + '/activity/app_car_house_loan/?promo_token=xmdj2',
			shareMainTit = '“车房贷”福利专享大放送',
			shareBody = '平台专用车库对质押车7*24小时监管（附图），标准资产更放心！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '“车房贷”福利专享大放送',
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
            mixins.shareData({title: '“车房贷”福利专享大放送', content: '平台专用车库对质押车7*24小时监管（附图），标准资产更放心！'});
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
                                url: '/api/activity/xiaomei/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1000'){
                                        mixins.registerApp({refresh:1, url:'/activity/app_pretty_reach_home/?promo_token=xmdj2'});
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
                        mixins.registerApp({refresh:1, url:'/activity/app_pretty_reach_home/?promo_token=xmdj2'});
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
                    url: '/api/activity/xiaomei/',
                    type: 'post',
                    success: function (data) {
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=xmdj2&next=/activity/app_pretty_reach_home/?promo_token=xmdj2'
                        }else if(data.ret_code=='1002'){
                            window.location.href = '/weixin/list/?promo_token=xmdj2'
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

    $('.popup_wrap .close_ico').click(function(){
        $('.popup_wrap').hide();
    });

    var speed = 100;//速度
    var time = "";//创建一个定时器
      $(function () {
        $(".choujiang").click(function() {//触发事件
          //$("#msgBox").fadeOut();
          doIt(1,1)//直接传入初始化参数，防止再次点击位置不对
        });
      });
      function doIt(t,i){//执行循环主方法
        time = setInterval(function () {
          i++;
          if (i > 8) {i = 1;t++;}
          $(".cj").removeClass("cur");
          $("#cj"+i).addClass("cur");
          getLb(t,i);
        }, speed);
      }
      function getLb(t,i){//中奖之后的处理
        console.log(t);
        console.log(i);
        if (t == 3) {
          if (i == 1) {//此处的i为设定的中奖位置，也可用ajax去请求获得
            clearInterval(time);
            //$("#msgBox").fadeIn().find("#text").html("恭喜你中奖了:第"+i+"！");
          }
        }
      }

    var swiper_1 = new Swiper('.swiper1', {
		pagination : '.pagination1',
		slidesPerView: 'auto',
        centeredSlides: true,
        paginationClickable: true,
        spaceBetween: 10,
		autoHeight: false
	});



})(org);
