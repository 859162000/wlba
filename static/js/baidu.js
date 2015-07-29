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
        registerTitle :'领取800元现金红包',    //注册框标语
        isNOShow : '1'
    });
    $('.receiveBtns').click(function(){
        var tag = $(this).attr('tag');
        if($('.banner-form').length >0){
            if(tag == '1'){
               window.location.href = '/'
            }else if(tag == '2'){
                $('#baiduAlert3').modal();
             }else{
                $('#baiduAlert2').modal();
            }
        }else{
            $('#baiduAlert1').modal();
        }
    })
    $('.alertBtn').click(function(){
        $('body,html').animate({scrollTop: 0}, 600);
        $.modal.close();
    })
    $('#receiveTwo').click(function(){
        var top = $('.activity-two-img').offset().top
        $('body,html').animate({scrollTop: top}, 600);
    })



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
    left2=backtop($(".baidu-content"));
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



