
(function(org) {
      var mp3 = document.getElementById("music"),play = $('#play');
        play.on('click', function (e) {
            if (mp3.paused) {
                mp3.play();
                $('#play').addClass('play_music').removeClass('close_music');
            } else {
                mp3.pause();
                $('#play').addClass('close_music').removeClass('play_music');
            }
        });

        mp3.play();
        $(document).one('touchstart', function () {
            mp3.play();
        });


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
                  shareName = '夹克的虾携手网利宝0元请您吃麻小',
                  shareImg = host + '/static/imgs/mobile_activity/app_jack_shrimp/300*300.png',
                  shareLink = host + '/activity/app_jack_shrimp/?promo_token=jkdx',
                  shareMainTit = '夹克的虾携手网利宝0元请您吃麻小',
                  shareBody = '网利宝与您激情无昼夜 快享欧洲杯';
              //分享给微信好友
              org.onMenuShareAppMessage({
                  title: shareMainTit,
                  desc: shareBody,
                  link: shareLink,
                  imgUrl: shareImg
              });
              //分享给微信朋友圈
              org.onMenuShareTimeline({
                  title: '夹克的虾携手网利宝0元请您吃麻小',
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



      wlb.ready({
        app: function (mixins) {
            mixins.shareData({title: '夹克的虾携手网利宝0元请您吃麻小！', content: '网利宝与您激情无昼夜 快享欧洲杯'});
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

                        $('.get_now').click(function(){
                            org.ajax({
                                url: '/api/activity/jiake/',
                                type: 'post',
                                success: function (data) {
                                    if(data.ret_code=='1000'){
                                        mixins.registerApp({refresh:1, url:'/activity/app_jack_shrimp/?promo_token=jkdx'});
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
                        mixins.registerApp({refresh:1, url:'/activity/app_jack_shrimp/?promo_token=jkdx'});
                    });
                } else {
                    login = true;
                    connect(data)

                }
            })

        },
        other: function(){
            $('.get_now').click(function(){
                org.ajax({
                    url: '/api/activity/jiake/',
                    type: 'post',
                    success: function (data) {
                        if(data.ret_code=='1000'){
                            window.location.href = '/weixin/regist/?promo_token=jkdx&next=/activity/app_jack_shrimp/?promo_token=jkdx'
                        }else if(data.ret_code=='1002'){
                            window.location.href = '/weixin/list/?promo_token=jkdx'
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
      $('#fullpage').fullpage({
            verticalCentered:false
      })
      $('.close_popup,.popup_button').click(function(){
        $('.popup_wrap,.popup_box').hide();
        $('.popup_wrap,.popup_box').hide();
      });

      $('.rule_span').click(function(){
          $('.popup_wrap').show();
      })






})(org);
