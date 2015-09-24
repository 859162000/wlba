(function(){
  //加息券规则
  $('#quan-rule1').on('click',function(){
    Down($('#ul-rule1'))
  })

  $('#quan-rule2').on('click',function(){
    Down($('#ul-rule2'))
  })
  $('#quan-rule4').on('click',function(){
    Down($('#ul-rule4'))
  })

  //下滑动画函数
  function Down(ele){
    var curHeight = ele.height();
    var autoHeight = ele.css('height', 'auto').height();
    if (!ele.hasClass('down')){
      ele.height(curHeight).animate({height: autoHeight},600,function(){
        ele.addClass('down')
      });
    }else{
      ele.height(curHeight).animate({height: 0},600,function(){
        ele.removeClass('down')
      });
    }
  }

  //点击立即领取
  $('.git-btn-fast').on('click',function(){
    if ($(this).attr('data-num')){
        window.location.href="/weixin/regist/?next=/activity/h5_mid_autumn/"
    }else{
      org.ajax({
          url: "/redpacket/apply/",
          type: "POST",
          data: { redpack_event_name : "2015中秋节80000加息券"},
          success: function(date){
            if (date['status']==true){
              $('.mid-modle').show();
              $('.mid-success').hide();
              $('#text').text('恭喜您～领取成功');
              $('#mid-fail').show();
            }else{
              $('.mid-modle').show();
              $('.mid-success').hide();
              $('#text').text('亲，不可重复领取');
              $('#mid-fail').show();
            }
          }
        })

    }
  })

  //立即投资按钮
  $('.touzi-btn').on('click',function(){
    if ($(this).attr('data-num')){
        window.location.href="/weixin/regist/?next=/activity/h5_mid_autumn/"
    }else{
      $('.mid-modle').show();
      $('#mid-fail').hide();
      $('.mid-success').show();
    }
  })

  $('.touzi-btn2').on('click',function(){
    if ($(this).attr('data-num')){
        window.location.href="/weixin/regist/?next=/activity/h5_mid_autumn/"
    }else{
      $('.mid-modle').show();
      $('#mid-fail').hide();
      $('.mid-success').show();
    }
  })

  //跳转投资页
  $('.success-btn').on('click',function(){
    window.location.href="/weixin/list/?next=/activity/h5_mid_autumn/"
  })

  //关闭模态框

  $('.mid-off,.success-btn').on('click',function(){
    $('.mid-modle').hide();
    $('#mid-fail').hide();
  })





})();