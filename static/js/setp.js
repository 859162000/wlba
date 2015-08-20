(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'activityRegister': 'activityRegister'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery','activityRegister'], function($,re) {
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'领取迅雷会员+现金红包',    //注册框标语
        isNOShow : '1',
        buttonFont: '立即注册'
    });

    var left2;
    left2=backtop($(".xingmei-content"));
    //浏览器大小改变触发的事件
    window.onresize = function(){
      left2 = backtop($(".gjw-gold"));
    };
    //赋值
    $('.xl-backtop').css({'left':left2});

    //显示微信二维码
   $('#xl-weixin').on('mouseover',function(){
     $('.erweima').show();
   });

    $('#xl-weixin').on('mouseout',function(){
     $('.erweima').hide();
   })

    //返回顶部
    $(window).scroll(function () {
        if ($(document).scrollTop() > 0) {
            $(".xl-backtop").fadeIn();
        }else{
            $('.xl-backtop').stop().fadeOut();
        }
    });

    $('.backtop').on('click',function(){
      $('body,html').animate({scrollTop: 0}, 600);
      return false
    })

  });

}).call(this);



