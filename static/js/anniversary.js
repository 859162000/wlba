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

  $(".rotateImgBtn").on('click',function() {
      $.ajax({
          url: '/api/celebrate/awards/',
          type: "POST",
          data: {
              action: 'IS_VALID'
          }
      }).done(function () {

      }).fail(function (xhr) {
          $(".rotateImgBtn").removeClass('.rotateImgBtn').addClass('rotateImg');
          //转盘
          $(".rotateImg").rotate({
              bind: {
                  click: function () {
                      var a = runzp(3);
                      $(this).rotate({
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
                          }
                      });
                  }
              }
          });
      });
    })
    //关闭中奖遮罩
    $('.spanBtn,.againBtn').on('click',function(){
        $('.page,.winningDiv').hide();
    })
    //非法用户
    $('#checkUserStatus').on('click',function(){
        $('.errorWin').modal();
    })
    //关闭弹框
    $('#closeWin').on('click',function(){
        $.modal.close()
    })

    $.ajax({
        url: '/api/celebrate/awards/',
        type: "POST",
        data: {
            action : 'IS_VALID'
        }
    }).done(function () {

    }).fail(function (xhr) {

    });

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

  });
}).call(this);



