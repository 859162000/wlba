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
			shareName = '全民淘金！',
			shareImg = host + '/static/imgs/mobile_activity/app_pretty_reach_home/300x300.jpg',
			shareLink = host + '/activity/app_gold_season/',
			shareMainTit = '全民淘金！',
			shareBody = '全民淘金！';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '全民淘金！',
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
            mixins.shareData({title: '全民淘金！', content: '全民淘金！'});
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
                    }
                })
            }
            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    $('.share-btns').on('click',function() {
                        mixins.loginApp({refresh: 1, url: 'https://staging.wanglibao.com/activity/app_gold_season/'});
                    })
                }else{
                    connect(data)
                    $('.share-btns').on('click',function(){
                        mixins.touchShare();
                    })
                }
            })

        },
        other: function(){
        }
    })


      var is_animate = true;

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

      function page_scroll() {
          $('.num-animate').each(function () {
              var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
              var key = parseInt($(this).attr('data-num'));
              $(this).prop('number', 0).animateNumber({
                  number: key,
                  numberStep: comma_separator_number_step
              }, 1000);
              is_animate = false;
          })
      }

      var windowHeight = $("body").height();
      var cheatseight = $(".cheats").height();
      var footerHeight = $(".cheats").height();
      var juli = windowHeight - cheatseight - footerHeight / 2 - 76;

      function button_fix() {
          if ($(window).scrollTop() >= juli) {
              $('.fixBox').css({'position': 'relative', 'background': 'none'});
          } else {
              $('.fixBox').css({'position': 'fixed', 'background': 'rgba(255,255,255,0.8)'});
          }
      }

      button_fix();
      $(window).scroll(function () {
          button_fix();
      });
      org.ajax({
          url: '/api/gettopofearings/',
          type: "POST",
          success:function(json){
          var rankingList_phone = [];
          var rankingList_amount = [];
          var json_one;
          for (var i = 0; i < json.records.length; i++) {
              json_one = json.records[i];
              if (json_one != '') {
                  var number = fmoney(json_one.amount, 0);
                  if (i <= 2) {
                      rankingList_phone.push(['<li class="front">' + json_one.phone + '</li>'].join(''));
                      rankingList_amount.push(['<li class="front"><span class="num-animate" data-num="' + json_one.amount + '">0</span> 元</li>'].join(''));
                  } else {
                      rankingList_phone.push(['<li>' + json_one.phone + '</li>'].join(''));
                      rankingList_amount.push(['<li><span class="num-animate" data-num="' + json_one.amount + '">0</span> 元</li>'].join(''));
                  }

              } else {
                  rankingList_phone.push(['<li>虚位以待</li>'].join(''));
                  rankingList_amount.push(['<li>虚位以待</li>'].join(''));
              }

          }
          $('.rankingList ul.two').html(rankingList_phone.join(''));
          $('.rankingList ul.three').html(rankingList_amount.join(''));
          page_scroll();
         }
      })
      var ipad = navigator.userAgent.match(/(iPad).*OS\s([\d_]+)/) ? true : false,
          iphone = !ipad && navigator.userAgent.match(/(iPhone\sOS)\s([\d_]+)/) ? true : false,
          ios = ipad || iphone;
      if (ios) {
          document.getElementById('ios-show').style.display = 'block';
      }
})(org);


