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

  //关闭弹出框
  $('.first-xl-off2,.reg-btn').on('click',function(){
    $('#small-zc').hide();
    $('#xl-aug-login').hide();
    $('#xl-aug-success').hide();
    $('#xl-aug-prize').hide();
  })


  //领取会员提示
    $('.setp-btn').on('click',function(){
      if ($(this).hasClass('receive')){
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

  //无线滚动
  var timer,i= 1,j=2;
  timer=setInterval(function(){
    scroll();
  },30)

  function scroll(){
    if (-parseInt($('.long-p').css('top'))>=$('.long-p p').height()){
      $('.long-p p').eq(0).appendTo($('.long-p'));
      $('.long-p').css({'top':'0px'})
      i=0
    }else{
      i++
      $('.long-p').css({'top':-i+'px'})
    }

  }


  //游戏
    //1,跑马灯
    setInterval(function(){
      $('.ring').css({'background':'url("/static/imgs/pc_activity/sept/ring-1.png") center center no-repeat'})
      setTimeout(function(){
        $('.ring').css({'background':'url("/static/imgs/pc_activity/sept/ring-2.png") center center no-repeat'})
        setTimeout(function(){
          $('.ring').css({'background':'url("/static/imgs/pc_activity/sept/ring-3.png") center center no-repeat'})
        },250)
      },250)
    },500)

    //按钮
    var num=1;
    var happy=random();
    console.log(happy)

    $('.game-btn').on('mousedown',function(){
      $('.game-btn').addClass('game-btn-down')

    });
    $('.game-btn').on('mouseup',function(){
      $('.game-btn').removeClass('game-btn-down')
      if ($(this).hasClass('go-game')){
        console.log(num)
        if (num>3){
          alert('机会已经用完了')
        }else{
          game();
        }
      }else{
        $('#small-zc').show();
        $('#xl-aug-login').show();
      }

    })
//    game();
    function game(){
      //按钮按下样式
      //手柄的样式
      setTimeout(function(){
        $('.side').addClass('side-down')
        setTimeout(function(){
          $('.side').removeClass('side-down')
          if (num!=happy){
            redpack('IGNORE_AWARD');
            star('0000');
          }else{
            redpack('GET_AWARD');
            star('1314');
          }

        },500)
      },1000)
    }



    //开始转动
    function star(a){
      var time,j=0;
      time=setInterval(function(){
        $('.long-sum').animate({'bottom':'-1062px'},100,function(){
          $('.long-sum').css({'bottom':'0px'})
        })
      },100)
      setTimeout(function(){
        for (var k= 0,len= a.length;k<len;k++){
          var g=9-a[k],b=k+1;
          $('.long-sum:eq('+k+')').css({'top':-g*178+'px'})
        }
        clearInterval(time)
        $('#rmb').text(a)
        $('#small-zc').show();
        if (a=='0000'){
          var txt=['你和大奖只是一根头发的距离','天苍苍，野茫茫，中奖的希望太渺茫','太可惜了，你竟然与红包擦肩而过'];
          var ind=parseInt(Math.random()*3);
          $('#xl-aug-success').hide();
          $('#xl-aug-prize p').text(txt[ind]);
          $('#xl-aug-prize').show();
        }else{
          $('#xl-aug-prize').hide();
          $('#xl-aug-success').show();
        }
        num++;
      },3000)
      $('.long-sum').css({'top':''});
      $('#chance').text(' '+3-num+' ')
    }

    //产生随机数,判断用户第几次抽中奖
    function random(){
      return parseInt(Math.random()*3+1)
    }
  //抽奖请求
  function redpack(sum){
    console.log(sum)
    $.ajax({
      url: "/api/xunlei/award",
      type: "POST",
      data: {action:sum}
    }).done(function(data) {
       console.log(data)
    });
  }



}).call(this);



