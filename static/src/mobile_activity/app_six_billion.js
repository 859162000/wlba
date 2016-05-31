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
			shareName = '一手解读',
			shareImg = host + '/static/imgs/mobile_activity/app_open_day_review/300*300.png',
			shareLink = host + '/activity/app_open_day_review/',
			shareMainTit = '一手解读',
			shareBody = '30秒看懂网利宝木材质押贷的前世今生';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '一手解读：木材质押贷的“前世今生”',
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
        spaceBetween: 10,
		autoHeight: false
	});
    var swiper_2 = new Swiper('.swiper2', {
		pagination : '.pagination2',
		slidesPerView: 'auto',
        centeredSlides: true,
        paginationClickable: true,
        spaceBetween: 10,
		autoHeight: false
	});

	var swiper_4 = new Swiper('.swiper_big', {
        pagination: '.swiper-pagination',
        slidesPerView: 'auto',
        centeredSlides: true,
        paginationClickable: true,
        spaceBetween: 10,
		autoHeight: false
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

                        $('.app_link').on("click",function(){
                        	mixins.jumpToManageMoney();
                        })
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
        //effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',

        onTouchEnd: function(swiper){
      }

	});
	/*轮播图结束*/

})(org);
