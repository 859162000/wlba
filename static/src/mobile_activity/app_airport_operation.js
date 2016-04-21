(function(org) {


	var sixlis = document.getElementById("six_lis");

     $('#sec').fullpage();
     sixlis.addEventListener("touchstart",function(){
          $(this).next().slideToggle();
      },false)


    var mp3 = document.getElementById("audios"),play = $('#audio');
    play.on('click', function (e) {
        if (mp3.paused) {
            mp3.play();
            $('#audio').removeClass("audio_off");
        } else {
            mp3.pause();
            $('#audio').addClass("audio_off");
        }
    });

    mp3.play();
    $(document).one('touchstart', function () {
        mp3.play();
    });

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
			shareName = '从容出行 尊贵定制',
			shareImg = host + '/static/imgs/mobile_activity/app_airport_operation/300x300.jpg',
			shareLink = host + 'weixin_activity/app_airport_operation/',
			shareMainTit = '从容出行 尊贵定制',
			shareBody = '网利宝携手空港易行狂撒出行卡';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '从容出行 尊贵定制',
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
	});

	$('.six_btn').on("click",function(){

            org.ajax({
                type: "post",
                url: "/api/activity/konggang/",
                dataType: 'json',
                success: function(data){
                    if(data.ret_code=='1000'){
                        window.location.href = '/weixin/login/?next=/activity/app_airport_operation/'
                    }else if(data.ret_code=='1002'){
                        $('.popup_box .main .textairport').text(''+data.message+'');
                        $('.popup_box').show();
                    }else if(data.ret_code=='0'){
                        $('.popup_box .main .textairport').text(''+data.message+'');
                        $('.popup_box').show();
                    }else if(data.ret_code=='1003'){
                        $('.popup_box .main .textairport').text(''+data.message+'');
                        $('.popup_box').show();
                    }

                    //console.log(data)
                }
            })
        })
        $('.popup_box .popup_button').click(function(){
            $('.popup_box').hide();
        });



})(org);


