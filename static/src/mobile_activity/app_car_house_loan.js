
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
                        function app_car_house_loan(){


                            org.ajax({
                                url: '/api/activity/chefangdai/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1002') {
                                        $('.section_2 .big_title').text(data.message);
                                        $('.luck_title_wrap').show();
                                        $('.popup_wrap dl').show();
                                        $('.popup_text').hide();
                                        $('.popup_button').text('马上去');
                                        $('.popup_button').click(function(){
                                            mixins.jumpToManageMoney();
                                        });
                                        $('.choujiang').click(function(){
                                            $('.popup_wrap').show();
                                        })
                                        ranking_list(data.rewards_list);
                                    }
                                    if(data.ret_code=='1000') {
                                        $('.section_2 .big_title').text(data.message);
                                        $('.popup_text').hide();
                                        $('.popup_wrap dl').show();
                                        $('.popup_button').text('马上去');
                                        $('.popup_button').click(function(){
                                            mixins.loginApp({refresh:1, url:'/activity/chefangdaiapp/'});
                                        });
                                        $('.choujiang').click(function(){
                                            $('.popup_wrap').show();
                                        })
                                        ranking_list(data.rewards_list);
                                    }
                                    if(data.ret_code=='1001') {
                                        $('.section_2 .big_title').text(data.message);
                                        $('.popup_wrap dl').show();
                                        $('.popup_button').text('马上去');
                                        $('.popup_button').click(function(){
                                             mixins.loginApp({refresh:1, url:'/activity/chefangdaiapp/'});
                                        });
                                        $('.choujiang').click(function(){
                                            $('.popup_wrap').show();
                                        })
                                    }
                                    if(data.ret_code=='0') {


                                            $('.section_2 .big_title').text(data.message);
                                            var speed = 100;//速度
                                            var time = "";//创建一个定时器
                                              $(function () {
                                                $(".choujiang").click(function() {//触发事件
                                                  $("#msgBox").fadeOut();
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
                                                //console.log(t);
                                                //console.log(i);
                                                if (t == 3) {
                                                  if (i == data.result_no) {//此处的i为设定的中奖位置，也可用ajax去请求获得
                                                    clearInterval(time);
                                                    $('.popup_wrap dl').hide();
                                                    $('.popup_text').text(data.content).show();
                                                    $('.popup_button').text('继续抽奖');
                                                    $('.popup_button').click(function(){
                                                        app_car_house_loan();
                                                        $('.popup_wrap ').hide();

                                                    });
                                                  }

                                                }
                                        }


                                    }



                                }
                            })
                        }
                        app_car_house_loan();
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

            car_house_loan();

        }
    })

    function car_house_loan(){
        org.ajax({
            url: '/api/activity/chefangdaiuserinfo/',
            type: 'post',
            success: function (data) {
                if(data.ret_code=='1002') {
                     $('.section_2 .big_title').text(data.message);
                    no_choujiang();
                    ranking_list(data.rewards_list);
                }
                if(data.ret_code=='1000') {
                     $('.section_2 .big_title').text(data.message);
                    no_denglu();
                    ranking_list(data.rewards_list);
                }
                if(data.ret_code=='1001') {
                     $('.section_2 .big_title').text(data.message);
                    no_denglu();
                }
                if(data.ret_code=='0') {
                     $('.section_2 .big_title').text(data.message);
                    choujiang(data.content,data.result_no);
                }


            }
        })
    }



    $('.popup_wrap .close_ico').click(function(){
        $('.popup_wrap').hide();
    });

    function no_choujiang(){
        $('.luck_title_wrap').show();
        $('.popup_wrap dl dt').text('您暂时还没有抽奖机会哦~');
        $('.popup_wrap dl dd').text('马上投资指定产品，获得更多抽奖机会！！');
        $('.popup_wrap dl').show();
        $('.popup_text').hide();
        $('.popup_button').text('马上去');
        $('.popup_button').click(function(){
            window.location.href = '/weixin/list/'
        });
        $('.choujiang').click(function(){
            $('.popup_wrap').show();
        })
    }

    function no_denglu(){
        $('.popup_text').hide;
        $('.popup_wrap dl dt').text('您还未登陆！');
        $('.popup_wrap dl dd').text('请登录后查看抽奖机会！');
        $('.popup_wrap dl').show();
        $('.popup_button').text('马上去');
        $('.popup_button').click(function(){
            window.location.href = '/weixin/regist/?next=/activity/chefangdaiapp/'
        });
        $('.choujiang').click(function(){
            $('.popup_wrap').show();
        })
    }


    function ranking_list(json){

        if(json.luck_list.length>0){
            var rankingList = [];
            var json_one;
            for(var i=0; i<1; i++){
                json_one = json.luck_list[i];

                var this_time = json_one.time;
                if(this_time>='86400'){
                    this_time = parseInt(this_time/86400)+'天'
                }else if(this_time>='3600'){
                    this_time = parseInt(this_time/3600)+'小时'
                }else if(this_time>='60'){
                    this_time = parseInt(this_time/60)+'分'
                }else{
                    this_time = parseInt(this_time)+'秒'
                }

                rankingList.push([''+json_one.phone.substring(0,3)+'****' +json_one.phone.substr(json_one.phone.length-4) +'获得'+json_one.name+''].join(''));

            }
            $('.horn span').html(rankingList.join(''));
            $('.horn').show();
        }else{

            $('.horn').hide();
        }
    }

    function choujiang(data_text,result_no){
        var speed = 100;//速度
        var time = "";//创建一个定时器
          $(function () {
            $(".choujiang").click(function() {//触发事件
              $("#msgBox").fadeOut();
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
            //console.log(t);
            //console.log(i);
            if (t == 3) {
              if (i == result_no) {//此处的i为设定的中奖位置，也可用ajax去请求获得
                clearInterval(time);
                $('.popup_wrap dl').hide();
                $('.popup_text').text(data_text).show();
                $('.popup_button').text('继续抽奖');
                $('.popup_wrap').show();
                car_house_loan();
                $('.popup_button').click(function(){
                    $('.popup_wrap ').hide();

                });
              }
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
