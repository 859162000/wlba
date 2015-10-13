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
        registerTitle :'注册送100元现金红包',    //注册框标语
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

      //关闭弹出框
    $('.first-xl-off2,.reg-btn').on('click',function(){
      $('#small-zc').hide();
      $('#xl-aug-login').hide();
      $('#xl-aug-success').hide();
      $('#xl-aug-prize').hide();
      $('#xl-aug-fail').hide();
    })



    //回到banner注册
    $('.setplogin').on('click',function(){
      $('#small-zc').hide();
      $('#xl-aug-login').hide();
      $('body,html').animate({scrollTop: 0}, 600);
      return false
    })

    //金币落下的效果

    var timer;
    timer=setInterval(function(){
      $('.money').animate({'top':'281px','left':'43px','display':'none'},500,function(){
        $('.money').css({'top':'135px','left':'-97px','display':'block'})
      })
    },1000)
    var change = [];
    redpack('ENTER_WEB_PAGE');
    $('.open-box-btn').on('click',function(){
        if ($(this).hasClass('received')){
            $('.center-box').addClass("big-box-open");
            $('.right-box').addClass("small-box-open1");
            //.big-box-open  small-box-open  .left-box  .right-box
        }else{
          $('#small-zc').show();
          $('#xl-aug-login').show();
        }

    })
    $('.ten-txtbutn').on('click',function(){
        if (change['ret_code']==4000){
          $('#small-zc').show();
          $('#xl-aug-fail p').text('Sorry~您不符合领奖条件');
          $('#xl-aug-fail').show();
        }else
        if ($(this).hasClass('received')){
          window.location.href="/"
        }else{
          $('#small-zc').show();
          $('#xl-aug-login').show();
        }

      })

    //回到banner注册
    $('.setplogin').on('click',function(){
      $('#small-zc').hide();
      $('#xl-aug-login').hide();
      $('body,html').animate({scrollTop: 0}, 600);
        return false
    })


      //请求宝箱接口
      redpack();
    function redpack(sum, callback){
      $.ajax({
        url: "/api/xunlei/award/",
        type: "POST",
        data: {action:sum},
        async: false
      }).done(function(data) {
         change = data;
          console.log(change);
        $('#chance').text(change['left']);

        callback && callback(data);

      });
    }


  });
}).call(this);
