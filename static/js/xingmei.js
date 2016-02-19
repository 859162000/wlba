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
        registerTitle :'注册送5元电影券',    //注册框标语
        isNOShow : '1',
        buttonFont: '注册领电影券',
        hasCallBack: true,
        callBack: function(){
          window.location.href='/';
        }
    });
    if($('#ganjiwang-model')){
      $('#ganjiwang-model,#ganjiwang-welcome').hide()
    }
    $('.xun-p a').attr('href','/accounts/login/?next=/activity/xingmei_two/?promo_token=xm2');
    $('.reg-btn').click(function(){
        $('body,html').animate({scrollTop: 0}, 600);
        $('#small-zc').hide();
        $('#xl-aug-success').hide()
    })
    //提醒注册
    $('.reg').on('click',function(){
      $('#small-zc').show();
      $('#xl-aug-success').show();
      $('#xl-aug-fail').hide();
    })
    //关闭模态框
    $('.first-xl-off2,.fail-btn').on('click',function(){
      $('#small-zc').hide();
      $('#xl-aug-success').hide();
      $('#xl-aug-fail').hide();
    })
    //提示

    //模态口
    var body_h=$('body').height();
    $('#small-zc').height(body_h);
     //固定回到顶部
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


    //请求接口,判断用户领奖的状态
    $('.xm-btn').on('click',function(){
      $.ajax({
        type: 'POST',
        data: {activity:'xm2'},
        url: '/api/activity/reward/',
        success: function(data){
          if(data.ret_code==1000){
            $('#xl-aug-success').show();
            $('#xl-aug-fail').hide()
          }else if(data.ret_code==1003){
            $('#xl-aug-fail').children('p').text('对不起,您不符合领取规则');
            $('#xl-aug-success').hide();
            $('#xl-aug-fail').show()
          }else if(data.ret_code==0){
            $('#xl-aug-fail').children('p').text('恭喜您,您已获得奖励,请到个人账户查看')
            $('#xl-aug-success').hide();
            $('#xl-aug-fail').show()
          }else{
            $('#xl-aug-fail').children('p').text(data.message)
            $('#xl-aug-success').hide();
            $('#xl-aug-fail').show()
          }
          $('#small-zc').show();
        }
      })


    })







  });

}).call(this);



