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
			shareName = '亿路旅程，亿同见证',
			shareImg = host + '/static/imgs/mobile/weChat_logo.png',
			shareLink = host + '/activity/six_billion/app/',
			shareMainTit = '亿路旅程，亿同见证',
			shareBody = '深情不及久伴，厚爱无需多言';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '亿路旅程，亿同见证',
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
		url: '/api/activity/hmd_invest_ranks/',
		type: 'get',
		success: function (json) {
			var rankingList = [];
			var json_one;
			if(json.hmd_ranks.length>0){
				for(var i=0; i<json.hmd_ranks.length; i++) {

					json_one = json.hmd_ranks[i];
					if (json_one != '') {
						var number = fmoney(json_one.amount__sum, 0);
						if (i < 3) {
							if (i == 0) {
								rankingList.push(['<li class="first"><div class="img"><img src="/static/imgs/mobile_activity/app_open_day_review/no_1.png"></div>'].join(''));
							} else if (i == 1) {
								rankingList.push(['<li class="second"><div class="img"><img src="/static/imgs/mobile_activity/app_open_day_review/no_2.png"></div>'].join(''));
							} else if (i == 2) {
								rankingList.push(['<li class="third"><div class="img"><img src="/static/imgs/mobile_activity/app_open_day_review/no_3.png"></div>'].join(''));
							}
							rankingList.push(['<div class="phone">' + json_one.phone.substring(0, 3) + '****' + json_one.phone.substr(json_one.phone.length - 4) + '</div><div class="money">'+number+'</div">'].join(''));

						} else {
							var i_num = i + 1;
							rankingList.push(['<li><div class="img"><img class="yuan" src="/static/imgs/mobile_activity/app_open_day_review/yuan.png"></div><div class="phone">' + json_one.phone.substring(0, 3) + '****' + json_one.phone.substr(json_one.phone.length - 4) + '</div><div class="money">'+number+'</div"></li>'].join(''));
						}
					}
				}
				$('.ranking_list ul').html(rankingList.join(''));
			}
		},error: function(data1){

		}
	})

    var swiper = new Swiper('.swiper1', {
		pagination : '.pagination1',
		slidesPerView: 'auto',
        centeredSlides: true,
        paginationClickable: true,
		autoHeight: false
	});


	var login = false;
    wlb.ready({

        app: function (mixins) {
			mixins.shareData({title: '亿路旅程，亿同见证', content: '深情不及久伴，厚爱无需多言'});
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
            })

        },
        other: function(){

        }
    })

	/*轮播图*/
	var swiper = new Swiper('.swiper1', {
		pagination: '.swiper-pagination',
		slidesPerView: 1,
        //effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto'

	});

	var swiper = new Swiper('.swiper2', {
		pagination: '.swiper-pagination2',
        slidesPerView: 1,
        //effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto'

	});

	var swiper = new Swiper('.swiper3', {
		pagination: '.pagination3',
		slidesPerView: 1,
        centeredSlides: true,
        paginationClickable: true

	});
	/*轮播图结束*/

	/*指定范围倒计时*/
	var time_intervalId;
	var curShowTimeSeconds = 0;
	//现在倒计时需要有多少秒
	var endTime = new Date(2016,5,3,18,00,00);
	//回头这里改成 2016,5,3,20,00,00

	var timestamp = Date.parse(new Date());
	//获得当前时间戳
	var timerFunction = function () {
		timestamp = Date.parse(new Date());
		if(timestamp>='1464919200000'){
		//2016年6月3日 10:00-18:00


			curShowTimeSeconds = getCurrentShowTimeSeconds();
			var hours = parseInt(curShowTimeSeconds/3600);
			var minutes = parseInt((curShowTimeSeconds - hours * 3600)/60);
			var seconds = curShowTimeSeconds % 60;

			$('.countdown_wrap .time_one_1').text(parseInt(hours/10));
			$('.countdown_wrap .time_one_2').text(parseInt(hours%10));

			$('.countdown_wrap .time_two_1').text(parseInt(minutes/10));
			$('.countdown_wrap .time_two_2').text(parseInt(minutes%10));

			$('.countdown_wrap .time_three_1').text(parseInt(seconds/10));
			$('.countdown_wrap .time_three_2').text(parseInt(seconds%10));
			if(Date.parse(new Date())>'1464948000000'){
				clearInterval(time_intervalId);
			}

		$('.countdown_wrap').show();

		}else{
			$('.countdown_wrap').hide();
		}
	}

	time_intervalId = setInterval(timerFunction, 1000);


	function getCurrentShowTimeSeconds(){
		var curTime = new Date();
		var ret = endTime.getTime() - curTime.getTime();
		//结束的时间减去现在的时间
		ret = Math.round(ret/1000);
		//把毫秒转化成秒

		return ret>=0 ? ret : 0;
		//ret大于等于0的话返回ret，如果不是返回0
		//如果倒计时结束，返回的结果是0
	}
	/*指定范围倒计时结束*/

})(org);
