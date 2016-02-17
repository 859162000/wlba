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
    $('.xun-p a').attr('href','/accounts/login/?next=/activity/xingmei_two/');
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
    $('.btn-fail').on('click',function(){
      $('#small-zc').show();
      $('#xl-aug-success').hide();
      $('#xl-aug-fail').show()

    })
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
    $.ajax({
      type: 'GET',
      url: '/api/activity/reward/?activity=xm2',
      success: function(data){
        console.log(data)
      },
      error: function(xhr, type){
        //alert('Ajax error!')
      }
    })





  });

}).call(this);



