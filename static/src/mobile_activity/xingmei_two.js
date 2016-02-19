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
        if(data.ret_code==1000){
          window.location.href='/weixin/regist/?next=/activity/app_xingmei_two/?promo_token=xm2'
        }else if(data.ret_code==1003){
          $('.xm-error').text('对不起,您不符合领取规则')
        }else if(data.ret_code==0){
          $('.xm-error').text('恭喜您,您已获得奖励,请到个人账户查看')
        }else{
          $('.xm-error').text(data.message)
        }
        $('.xm-error').show()
      }
    })
  })
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



})();

