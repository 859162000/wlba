// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
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
    left2=backtop($(".gjw-gold"));
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
        } else if ($(document).scrollTop() <= 0) {
            $('.xl-backtop').stop().fadeOut();
        }
    });

    $('.backtop,#go-top').on('click',function(){
      $('body,html').animate({scrollTop: 0}, 600);
      return false
    })
    //模态口
    var body_h=$('body').height();
    $('#small-zc').height(body_h);
    //关闭模态窗
    $('.first-xl-off,.first-xl-off2,.look,.agin,#go-top').on('click',function(){
      $('#small-zc').hide();
    });

//    $('#small-zc').on('click',function(){
//      $('#small-zc').hide();
//    });
    //阻止冒泡
     $('.xl-box1,#seven-success,#first-redpack-fail,#xl-aug-success,#aug-box1').on('click',function(event){
       if (event.stopPropagation){
         event.stopPropagation();
       }else{
         event.cancelBubble = true;
       }

     });
    //关闭提示
    $('.xl-off2').on('click',function(){
      $('#first-redpack-fail').hide()
    })

    //请求
    $.ajax({
      url: "/api/xunlei/august/count/",
      type: "GET"
    }).done(function(data) {
      var number=parseInt(data['num']);
        var rednum=16329+number;
        var str=rednum.toString();
        for (var i=2,len= str.length;i<=len;i++){
          $('.scroll').append($('#view').clone(true));
        }
        for (var j=0,len2= str.length;j<=len2;j++){
          var this_index=str[j];
          $('.long').eq(j).animate({bottom:-this_index*58+'px'},500);
        }
    });
    //点击旅游路线
    $('#tour_line').on('click',function(){
      $('.gjw-tour').slideToggle(300)
    })

    //点击领取(1)
    $('.aut-give').on('click',function(){
      if ($(this).hasClass('aut-notgive')){
        $('#small-zc').show();
      }else{
        $.ajax({
          url: "/api/xunlei/8/check/",
          type: "GET"
        }).done(function(date) {
          $('#small-zc').show();
          $('#aug-box1').hide();
          $('#seven-success').hide();
          $('#xl-aug-success').hide();
          if (date['ret_code']==1){
            $('#first-redpack-fail').children('p').text(date['message']);
            $('#first-redpack-fail').show();
          }else if (date['ret_code']==2){
            $('#first-redpack-fail').children('p').text(date['message']);
            $('#first-redpack-fail').show();
          }else if (date['ret_code']==0){
            if (date['data']['has_rewarded']==false){
              $('#seven-success').show();
            }else if (date['data']['has_rewarded']==true){
              $('#first-redpack-fail').children('p').text('不能重复领取');
              $('#first-redpack-fail').show();
            }
          }

        });
      }
    })

    //点击领取(2)
    $('.aut-cz').on('click',function(){
      if ($(this).hasClass('aut-notcz')){
        $('#small-zc').show();
      }else{
        $('#small-zc').show();
        $('#aug-box1').hide();
        $('#seven-success').hide();
        $('#xl-aug-success').children('p').html('<span>首次充值</span>送迅雷白金会员<br><b>充值完成系统自动发放</b>');
        $('#fast').text('赶快去充值');
        $('#xl-aug-success').show();
      }
    })
    //点击领取(3)
    $('.aug-touz').on('click',function(){
      if ($(this).hasClass('aug-nottouz')){
        $('#small-zc').show();
      }else{
        $('#small-zc').show();
        $('#aug-box1').hide();
        $('#seven-success').hide();
        $('#xl-aug-success').children('p').html('<span>投资</span>送一年迅雷白金会员')
        $('#fast').text('赶快去投资')
        $('#xl-aug-success').show();
      }
    })

    //点击领取(4)
    $('#aut-tour ').on('click',function(){
      var re_top2=$('#tour').offset().top;
      $('body,html').animate({scrollTop:re_top2}, 600);
      return false
    })

    //马上报名
    $('.xl-aug-btn1').on('click',function(){
      if ($(this).hasClass('go')){
        $('#small-zc').show();
      }else{
        $('#small-zc').show();
        $('#aug-box1').hide();
        $('#seven-success').hide();
        $('#xl-aug-success').children('p').html('首次投资网利宝<span>单笔满10000元</span><br><b>可获得一次免费旅游的机会</b>')
        $('#fast').text('赶快去投资')
        $('#xl-aug-success').show();
      }
    })

    $('#fast').on('click',function(){
      if($(this).text()=='赶快去充值'){
        window.location.href='/pay/banks/'
      }
      if($(this).text()=='赶快去投资'){
        window.location.href='/p2p/list/'
      }
    })
    //倒计时
    count_down = function(o) {
      var sec, timer;
      sec = (new Date(o.replace(/-/ig, '/')).getTime() - new Date().getTime()) / 1000;
      sec = parseInt(sec);
      timer = setTimeout((function() {
        count_down(o);
      }), 1000);
      if (sec <= 0) {
        $('#small-zc').show();
        $('#box1').hide();
        $('#activity-over').show();
      }
    };

    count_down('2015-09-30 00:00:00')


  });

}).call(this);


//# sourceMappingURL=login_modal.js.map

