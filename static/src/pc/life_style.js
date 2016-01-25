/**
 * Created by rsj217 on 16-1-21.
 */
(function(){

//  $('#fullpage').fullpage();
  //banner height


  var h_win = $(window).height();
  var Top = $('.banner').offset().top;
  var H = h_win-Top;
  $('.banner').height(H+'px');
  $('.main-box').height(h_win-170+'px');
  $('.main-box .lei-box').height(h_win-200+'px')
  var T = $('.main-box').height()/2-67+'px';
  $('.fp-prev,.fp-next').css({'top':T});






//  alert(H)

//  $('.main-box').height('663px');
//  $('.main-box .lei-box').height('663px');

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
       point()
     }else if($(this).index() == 1){
       $('#them-box').show();
       $('#lei-box').hide();
       $('#heart-box').hide();
       $('.ul-point').attr('data-num','them-box')
       point();
       tab('#them-box');
     }else{
       $('#heart-box').show();
       $('#lei-box').hide();
       $('#them-box').hide();
       $('.ul-point').attr('data-num','heart-box')
       point()
       tab('#heart-box');
     }
  })

//判断点儿的个数
  function point(){
    var _id = $('.ul-point').attr('data-num');
    var _leng = $('#'+_id).children('.slide').length;
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
    $('.fp-next').on('click',function(){
      sum++;
      if(sum==$(ele).children('.slide').length){
        sum = 0;
        $(ele).animate({'left':'0px'})
      }
      $(ele).animate({'left':-1100*sum+'px'})
      $('.ul-point ul li').eq(sum).addClass('point-hight').siblings().removeClass('point-hight');
    });
    $('.fp-prev').on('click',function(){
      sum--;
      if(sum<0){
        sum = $(ele).children('.slide').length-1;
        $(ele).animate({'left':-1100*sum+'px'})
      }else{
        $(ele).animate({'left':-1100*sum+'px'})
      }

      $('.ul-point ul li').eq(sum).addClass('point-hight').siblings().removeClass('point-hight');
    });


  }

//全屏滚动
    var body_height=$('body,html').height();
    var slide_height = $('.main-box').height();
    var footer_height = $('#footer').height();


    var sum = 0;



    $(window).scroll(function(){
        if (sum == 0 && $(window).scrollTop()>50){
            $('body,html').stop().animate({'scrollTop':h_win+'px'},80,function(){
                sum = 1;
            })
        }else if(sum ==1 && $(window).scrollTop()<h_win){
            $('body,html').stop().animate({'scrollTop':0+'px'},80,function(){
                sum = 0;
            })
        }

        if(sum == 1  && $(window).scrollTop()>h_win){
            $('body,html').stop().animate({'scrollTop':(h_win+footer_height)+'px'},50,function(){
                sum = 2;
            })
        }
//        console.log(sum+'==='+$(window).scrollTop());

//        console.log($(window).scrollTop()+'=='+$(".main").attr('data-num'));
//        console.log(sum);

        if(sum == 2  && $(window).scrollTop()<(h_win+footer_height)){
            $('body,html').stop().animate({'scrollTop':h_win+'px'},50,function(){
                sum = 3;
            })
        }else if(sum ==3 && $(window).scrollTop()>h_win){
            $('body,html').stop().animate({'scrollTop':(h_win+footer_height)+'px'},80,function(){
                sum = 2;
            })
        }

        if(sum == 3 && $(window).scrollTop()<h_win){
            $('body,html').stop().animate({'scrollTop':0+'px'},50,function(){
                sum = 0;
            })
        }

    });





})();

//var h_win=window.innerHeight;
//var sum = 0;
// var scrollFunc=function(e){
//
//  e=e || window.event;
//  if(e.wheelDelta){//IE/Opera/Chrome
//    if(e.wheelDelta==120)
//    {
//      //向上滚动事件
////      alert(e.wheelDeta +"向下");
//      $('body,html').animate({'scrollTop':0},200)
//
//    }else
//    {
//      //向上滚动事件
////      alert(e.wheelDeta +"向上");
//      $('body,html').animate({'scrollTop':h_win},200)
//      sum++;
//      console.log(sum)
//      if(sum>2){
//        $('body,html').animate({'scrollTop':$('body,html').height()},200)
//
//      }
//
//    }
//  }else if(e.detail){
//    //Firefox
//    if(e.detail==-3) {
//      //向上滚动事件<br>
//      alert(e.detail +"向上");
//
//    }else {
//      //向下滚动事件<br>
//      alert(e.detail +"向下 ");
//
//    }
//  }
// };
// if(document.addEventListener){
//  //adding the event listerner for Mozilla
//   document.addEventListener("DOMMouseScroll" ,scrollFunc, false);
//   }
//   //IE/Opera/Chrome
//   window.onmousewheel=document.onmousewheel=scrollFunc;


