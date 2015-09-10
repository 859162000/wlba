(function() {
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'jqueryRotate' : 'jQueryRotate.2.2',
        'script' : 'script',
        tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jqueryRotate' : ['jquery']
    }
  });

  require(['jquery','jqueryRotate','script',"tools"], function($,jqueryRotate,script,tool) {
      var index = 0,leftM = 0;
      //转盘
      $(".rotateImg").rotate({
          bind: {
              click: function () {
                  if(!$(".rotateImg").hasClass('rotateImgNo')){
                      if(leftM > 0) {
                         $.ajax({
                            url: '/api/celebrate/awards/',
                            type: "POST",
                            data: {
                                action : 'AWARD_DONE'
                            }
                         }).done(function (xhr) {
                           $(".rotateImg").addClass('rotateImgNo');
                             if(xhr.ret_code == '3016') {
                                $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                                $('.errorWin').modal();
                             }else{
                                 if (xhr.left >= 0) {
                                     if (xhr.amount == 50.00) {
                                         index = 3
                                     } else if (xhr.amount == 200.00) {
                                         index = 2
                                     } else if (xhr.amount == 500.00) {
                                         index = 1
                                     } else if (xhr.amount == 1000.00) {
                                         index = 0
                                     }
                                     var a = runzp(index);
                                     $('.rotateImg').rotate({
                                         duration: 3000,
                                         angle: 0,
                                         animateTo: 1440 + a.angle,
                                         callback: function () {
                                             $('.page,.winningDiv').show();
                                             $('#moeny').text(a.prize);
                                             var top = $('.luckDrawLeft').offset().top;
                                             var left = $('.luckDrawLeft').offset().left;
                                             $('.winningDiv').css({
                                                 'top': top + 122,
                                                 'left': left + 164
                                             })
                                             $('.page').width(document.body.clientWidth);
                                             $('.page').height(document.body.clientHeight);
                                             $(".rotateImg").removeClass('rotateImgNo');
                                             leftM--
                                         }
                                     });
                                 } else {
                                     $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                                     $('.errorWin').modal();
                                 }
                             }
                         })
                      }else{
                         $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                         $('.errorWin').modal();
                      }
                  }
              }
          }
      });
    //关闭中奖遮罩
    $('.spanBtn,.againBtn').on('click',function(){
        $('.page,.winningDiv').hide();
    })
    //非法用户
    $('#checkUserStatus').on('click',function(){
        if($(this).hasClass('newUser')){
          $('.errorWin').find('#errorContent').text('不能重复领取～亲');
        }else{
          $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
        }
        $('.errorWin').modal();
    })
    //关闭弹框
    $('#closeWin').on('click',function(){
        $.modal.close()
    })

    //初始化数据
    $.ajax({
        url: '/api/celebrate/awards/',
        type: "POST",
        data: {
            action : 'IS_VALID'
        }
    }).done(function (xhr) {
       //有效用户
       if(xhr.ret_code == '3001'){
         $.ajax({
            url: '/api/celebrate/awards/',
            type: "POST",
            data: {
                action : 'ENTER_WEB_PAGE'
            }
         }).done(function (xhr) {
             leftM = xhr.left;
         })
         $('#checkUserStatus').addClass('newUser')
       }else if(xhr.ret_code == '3000'){
        //非法用户
        $('#checkUserStatus').addClass('oldUser')
       }
    })

    //中奖名单
    $.ajax({
        url: '/api/celebrate/awards/',
        type: "POST",
        data: {
            action : 'GET_AWARD'
        },
        async: false
     }).done(function (xhr) {
        var htmlStr = '',j = 0;
        if(xhr.data.length > 0){
            $.each(xhr.data,function(i,o){
                i % 2 == 0 ? oddStyle = 'odd' : oddStyle ='';
                if( i != 0 ){
                    if(i % 5 == 0){
                        j++;
                        if(j == 1){
                           htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>135****2035</em>获得</span><label>200元红包</label></li>';
                        }else if(j == 2){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>186****0386</em>获得</span><label>500元红包</label></li>';
                        }else if(j == 3){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>150****7917</em>获得</span><label>Beats耳机</label></li>';
                        }else if(j == 4){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>189****2528</em>获得</span><label>电动滑板车</label></li>';
                        }else if(j == 5){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>133****0525</em>获得</span><label>Beats耳机</label></li>';
                        }else if(j == 6){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>182****7831</em>获得</span><label>500元红包</label></li>';
                        }else if(j == 7){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>188****5117</em>获得</span><label>乐视电视</label></li>';
                        }else if(j == 8){
                             htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>138****1219</em>获得</span><label>1000元红包</label></li>';
                             j = 0;
                             return true;
                        }
                    }else{
                         htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>'+ o.phone.substring(0,3) +'****'+  o.phone.substring(7,12) +'</em>获得</span><label>'+ o.awards +'元红包</label></li>';
                    }
                }else{
                    htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>'+ o.phone.substring(0,3) +'****'+  o.phone.substring(7,12) +'</em>获得</span><label>'+ o.awards +'元红包</label></li>';
                }
            })
            $('#users').append(htmlStr);
        }
     })

    //无线滚动
    var timer,i= 1,j=2;
    timer=setInterval(function(){
      scroll();
    },30)

    function scroll(){
      if (-parseInt($('#users').css('top'))>=$('#users li').height()){
        $('#users li').eq(0).appendTo($('#users'));
        $('#users').css({'top':'0px'})
        i=0
      }else{
        i++
        $('#users').css({'top':-i+'px'})
      }

    }
    var width = $('body').width();
    $('.wanglibao img').css({
        'width': width*0.035 +'%'
    })

     //固定回到顶部
     function backtop(){
       var k=document.body.clientWidth,
         a = k - 100
       return a;
     }
    var left2;
    left2=backtop();
    //浏览器大小改变触发的事件
    window.onresize = function(){
      left2 = backtop();
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