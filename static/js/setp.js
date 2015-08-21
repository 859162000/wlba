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
    //回到顶部开始
    //固定回到顶部,
     function backtop(box){
       var k=document.body.clientWidth,
         e=box.width();
         q=k-e;
         w=q/2;
         r= e+w;
         a=r+20+'px';
       return a;
     }
    var left2;
    left2=backtop($(".setp-content"));
    console.log(left2)
    //浏览器大小改变触发的事件
    window.onresize = function(){
      left2 = backtop($(".setp-content"));
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

    //回到顶部结束

    //模态口高度
    var body_h=$('body').height();
    $('#small-zc').height(body_h);
  });

}).call(this);



