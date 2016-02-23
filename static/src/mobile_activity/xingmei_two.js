/**
 * Created by rsj217 on 16-2-18.
 */



(function(){
  $('.reg-btn').on('click',function(){
    org.ajax({
      type: 'POST',
      data: {activity:'xm2'},
      url: '/api/activity/reward/',
      success: function(data){
        console.log(data.ret_code)
        if(data.ret_code==1000){
          window.location.href='/weixin/regist/?next=/activity/app_xingmei_two/&mobile=/weixin/list/?promo_token=xm2'
        }else if(data.ret_code==1003){
          $('.xm-error').text('来晚了,电影券已经抢光了')
          $('.xm-error').show()
        }else if(data.ret_code==1005){
          $('.xm-error').text('您的奖励已发放')
          $('.xm-error').show()
        }else if(data.ret_code==0){
          $('.xm-error').text('恭喜您,您已获得奖励,请到个人账户查看')
          $('.xm-error').show()
        }else{
          $('.xm-error').text(data.message)
          $('.xm-error').show()
        }
      }
    })
  })
  //微信分享
  var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
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
  wx.ready(function() {
    var host = 'https://staging.wanglibao.com',
      shareImg = host + '/static/imgs/mobile/share_logo.png',
      shareLink = host + '/activity/app_xingmei_two/?promo_token=xm2',
      shareMainTit = '你观影，我买单',
      shareBody = '去星美看电影，来网利宝免费领票';
    //分享给微信好友
    org.onMenuShareAppMessage({
      title: shareMainTit,
      desc: shareBody,
      link: shareLink,
      imgUrl: shareImg
    });
    //分享给微信朋友圈
    org.onMenuShareTimeline({
      title: shareMainTit,
      link: shareLink,
      imgUrl: shareImg
    })
    //分享给QQ
    org.onMenuShareQQ({
      title: shareMainTit,
      desc: shareBody,
      link: shareLink,
      imgUrl: shareImg
    })
  });



})();

