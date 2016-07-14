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
			shareName = '“爱妻悦”—爱无价 “妻”悦享',
			shareImg = host + '/static/imgs/mobile/weChat_logo.png',
			shareLink = host + '/activity/app_love_on_july/',
			shareMainTit = '“爱妻悦”—爱无价 “妻”悦享',
			shareBody = '七月把最好的爱送给心爱的她，爱她就努力赚，爱她就让“她”乐开花！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '“爱妻悦”—爱无价 “妻”悦享',
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

	function fmoney(s, type) {
		if (/[^0-9\.]/.test(s))
			return "0";
		if (s == null || s == "")
			return "0";
		s = s.toString().replace(/^(\d*)$/, "$1.");
		s = (s + "00").replace(/(\d*\.\d\d)\d*/, "$1");
		s = s.replace(".", ",");
		var re = /(\d)(\d{3},)/;
		while (re.test(s))
			s = s.replace(re, "$1,$2");
		s = s.replace(/,(\d\d)$/, ".$1");
		if (type == 0) {// 不带小数位(默认是有小数位)
			var a = s.split(".");
			if (a[1] == "00") {
				s = a[0];
			}
		}
		return s;
	}



	$.ajax({
		url: '/api/july_reward/fetch/',
		type: 'post',
		success: function (json) {
			var rankingList = [];
			var json_one;
			if(json.dayranks.length>0){
				for(var i=0; i<json.dayranks.length; i++) {

					json_one = json.dayranks[i];
					if (json_one != '') {
						var number = fmoney(json_one.amount__sum, 1);

						if (i < 3) {
							if (i == 0) {
								rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/mobile_activity/app_love_on_july/img13_13.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num money_num1">'+number+'元</div></div>'].join(''));
							} else if (i == 1) {
								rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/mobile_activity/app_love_on_july/img13_15.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num money_num2">'+number+'元</div></div>'].join(''));
							} else if (i == 2) {
								rankingList.push(['<div class="box"><div class="name_text">'+json_one.sex+'</div><img src="/static/imgs/mobile_activity/app_love_on_july/img13_17.png"><div class="phone_num">'+json_one.phone+'</div><div class="money_num money_num3">'+number+'元</div></div>'].join(''));
							}

						} else {

						}
					}
				}
				$('.now_ranking_main .box_wrap').html(rankingList.join(''));
			}

		},error: function(data1){

		}
	})

	var login = false;
    wlb.ready({

        app: function (mixins) {
			mixins.shareData({title: '“爱妻悦”—爱无价 “妻”悦享'});
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

                        //$('.app_link').on("click",function(){
                        //	mixins.jumpToManageMoney();
                        //})
                    }
                })
            }
            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    login = false;
                } else {
                    login = true;
                    connect(data)

                }
				$('.href_link').click(function(){
					mixins.jumpToManageMoney();
				})
            })

        },
        other: function(){
			$('.href_link').click(function(){
				window.location.href = '/weixin/list/'
			})
        }
    })

	/*轮播图*/
	var swiper = new Swiper('.swiper1', {
		pagination: '.pagination1',
		slidesPerView: 1,
        //effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto'

	});

	/*轮播图结束*/

	var oDate = new Date(); //实例一个时间对象；
	var nian = oDate.getFullYear();   //获取系统的年；
	var yue = oDate.getMonth()+1;   //获取系统月份，由于月份是从0开始计算，所以要加1
	var ri = oDate.getDate(); // 获取系统日，
	var shi = oDate.getHours(); //获取系统时，
	var fen = oDate.getMinutes(); //分
	oDate.getSeconds(); //秒

	function bu_ling(s) {
		return s < 10 ? '0' + s: s;
	}

	$('#act_time').text('截止 '+nian+'.'+bu_ling(yue)+'.'+bu_ling(ri)+' '+bu_ling(shi)+':'+bu_ling(fen)+'');

	$('.wenhao').click(function(){
		$('.popup_wrap').show();
	});
	$('.popup_wrap .main .close_popup').click(function(){
		$('.popup_wrap').hide();
	});
})(org);
