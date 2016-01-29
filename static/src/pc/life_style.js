/**
 * Created by rsj217 on 16-1-21.
 */

var video_1 = document.getElementById('really-cool-video'),
    video_2 = document.getElementById('really-cool-video2');
// 原生的JavaScript事件绑定函数
  function bindEvent(ele, eventName, func){
      if(window.addEventListener){
          ele.addEventListener(eventName, func);
      }
      else{
          ele.attachEvent('on' + eventName, func);
      }
  }

  bindEvent(video_1,'ended',function(){
    document.getElementsByClassName('vjs-poster')[0].style.display='block';
    document.getElementsByClassName('vjs-big-play-button')[0].style.display='block';
    video_1.currentTime = 0;
  });

  bindEvent(video_1,'play',function(){
    document.getElementsByClassName('vjs-poster')[0].style.display='none';
    document.getElementsByClassName('vjs-big-play-button')[0].style.display='none';
  });

   bindEvent(video_2,'ended',function(){
      document.getElementsByClassName('vjs-poster')[1].style.display='block';
      document.getElementsByClassName('vjs-big-play-button')[1].style.display='block';
      video_2.currentTime = 0;
    });

    bindEvent(video_2,'play',function(){
      document.getElementsByClassName('vjs-poster')[1].style.display='none';
      document.getElementsByClassName('vjs-big-play-button')[1].style.display='none';
    });


require.config({
  paths: {
    'scrollify': 'lib/jquery.fullPage.min',
    'videojs': 'lib/video.min'
  },
  shim: {
    'scrollify': ['jquery']
  }
});

require(['jquery','videojs','scrollify'], function($, videojs, scrollify) {
  //视屏播放
//  $('#really-cool-video').height(283);
//  $('#really-cool-video2').height(283);
//  var player = videojs('really-cool-video', { /* Options */ }, function() {
//    console.log('Good to go!');
//
//
//  });





  $('.tv-box1').on('click',function(){
    $(this).children('.black').hide()
  })

  //判断高度
  var _index = $(".section").length-1;
  $('.tv-box1,.tv-box2').css({"height":355});
  $('.show-box h1').css({"height":$(window).height()/4});

  $('#fullpage').fullpage({
    normalScrollElements :'#main-box',
    afterLoad : function(anchorLink,index){
      if (index == 1){
        $(".section").eq(1).show();
      }else if (index ==2){
        $(".section").eq(2).show();
      }

    },
    navigation : true

  });

  var h_win = $(window).height();
  var Top = $('.banner').offset().top;
  var H = h_win-Top;
  $('.banner').height(H+'px');
  $('.main-box').height(h_win-130+'px');
  $('.main-box .lei-box').height(h_win-180+'px');
  var T = $('.main-box').height()/2-67+'px';
  $('.fp-prev,.fp-next').css({'top':T});



//划过加样式
  $('.life_nav ul li').hover(function(){
     if($(this).index() == 0){
       $(this).children('span').addClass('icon1_hover')
     }else if($(this).index() == 1){
       $(this).children('span').addClass('icon2_hover')
     }else{
       $(this).children('span').addClass('icon3_hover')
     }
  },function(){
    if($(this).index() == 0){
       $(this).children('span').removeClass('icon1_hover')
     }else if($(this).index() == 1){
       $(this).children('span').removeClass('icon2_hover')
     }else{
       $(this).children('span').removeClass('icon3_hover')
     }

  })

//点击加样式
  $('.life_nav ul li').eq(0).children('img').show();
  $('.life_nav ul li').on('click',function(){
     $(this).children('img').show();
     $(this).siblings().children('img').hide();
  })
point();
//点击显示相应内容
  $('.life_nav ul li').on('click',function(){
     if($(this).index() == 0){
       $('#lei-box').show();
       $('#them-box').hide();
       $('#heart-box').hide();
       $('.ul-point').attr('data-num','lei-box')
       point();
     }else if($(this).index() == 1){
       $('#them-box').show();
       $('#lei-box').hide();
       $('#heart-box').hide();
       $('.ul-point').attr('data-num','them-box')
       point();
     }else{
       $('#heart-box').show();
       $('#lei-box').hide();
       $('#them-box').hide();
       $('.ul-point').attr('data-num','heart-box')
       point();
     }
  })

//判断点儿的个数
  function point(){
    var _id = $('.ul-point').attr('data-num');
    var _leng = $('#'+_id).children('.slide-div').length;
    var str = '';
    for(var i=0;i<_leng;i++){
      str+='<li></li>'

    }
    $('.ul-point ul').html(str)
    $('.ul-point ul li').eq(0).addClass('point-hight')
    tab('#'+_id,0)
  }

//tab切换
  function tab(ele,number){
    var sum = number;
    $(ele).css({'left':'0px'});
    $('.next').off().on('click',function(){
      $(this).removeClass('next');
      sum++;
      if(sum==$(ele).children('.slide-div').length){
        sum = 0;
        $(ele).animate({'left':'0px'},function(){
          $('.fp-next').addClass('next')
        })
      }
      $(ele).animate({'left':-1100*sum+'px'},function(){
          $('.fp-next').addClass('next')
        })
      $('.ul-point ul li').eq(sum).addClass('point-hight').siblings().removeClass('point-hight');
    });
    $('.prev').off().on('click',function(){
      $(this).removeClass('prev');
      sum--;
      if(sum<0){
        sum = $(ele).children('.slide-div').length-1;
        $(ele).animate({'left':-1100*sum+'px'},function(){
          $('.fp-prev').addClass('prev');
        })
      }else{
        $(ele).animate({'left':-1100*sum+'px'},function(){
          $('.fp-prev').addClass('prev');
        })
      }

      $('.ul-point ul li').eq(sum).addClass('point-hight').siblings().removeClass('point-hight');

    });

    $('.ul-point ul li').on('click',function(){
      sum = $(this).index();
      $(this).addClass('point-hight').siblings().removeClass('point-hight');
      $(ele).animate({'left':-1100*sum+'px'})


    })


  }







});



