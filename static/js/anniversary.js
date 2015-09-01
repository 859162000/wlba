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
      //转盘
      $(".rotateImg").rotate({
          bind: {
              click: function () {
                   $.ajax({
                        url: '/api/celebrate/awards/',
                        type: "POST",
                        data: {
                            action : 'ENTER_WEB_PAGE'
                        }
                     }).done(function (xhr) {
                       if(xhr.left > 0){
                        var a = runzp(3);
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
                          }
                        });
                       }else{
                           $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                           $('.errorWin').modal();
                       }
                     }).fail(function (xhr) {

                     });
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

    $.ajax({
        url: '/api/celebrate/awards/',
        type: "POST",
        data: {
            action : 'IS_VALID'
        }
    }).done(function (xhr) {
       if(xhr.ret_code == '3001'){
         $.ajax({
            url: '/api/celebrate/awards/',
            type: "POST",
            data: {
                action : 'ENTER_WEB_PAGE'
            }
         }).done(function () {
            $('.rotateImgBtn').removeClass('rotateImgBtn').addClass('rotateImg');
         }).fail(function (xhr) {

         });
         $('#checkUserStatus').addClass('newUser')
       }else if(xhr.ret_code == '3000'){
        $('#checkUserStatus').addClass('oldUser')
       }
    }).fail(function (xhr) {

    });

    $.ajax({
        url: '/api/xunlei/award/records/',
        type: "POST",
        data: {
            action : 'ENTER_WEB_PAGE'
        },
        async: false
     }).done(function (xhr) {
        var htmlStr = '';
        $.each(xhr.data,function(i,o){
            i % 2 == 0 ? oddStyle = 'odd' : oddStyle ='';
;           htmlStr+='<li class='+ oddStyle +'><span>恭喜<em>'+ o.phone.substring(0,3) +'******'+  o.phone.substring(9,11) +'</em>获得</span><label>'+ o.awards +'元红包</label></li>'
        })
        $('#users').append(htmlStr);
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

  });
}).call(this);



