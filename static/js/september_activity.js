(function(){
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'jqueryRotate' : 'jQueryRotate.2.2',
        'script' : 'sep_script',
        tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.easing' : ['jquery'],
      'jqueryRotate' : ['jquery']
    }
  });
  require(['jquery','jqueryRotate','script',"tools"], function($,jqueryRotate,easing,script,tool) {
    //转盘
    $(".rotateImg").rotate({
      bind:{
        click:function(){
		  var a = runzp(3);
		  $(this).rotate({
		    duration:3000,
			angle: 0,
            animateTo:1440+a.angle,
			easing: $.easing.easeOutSine,
			callback: function(){
              $('.page,.winningDiv').show();
              $('#moeny').text(a.prize);
              var top = $('.luckDrawLeft').offset().top;
              var left = $('.luckDrawLeft').offset().left;
              $('.winningDiv').css({
                'top' :top+122,
                'left':left+164
              });
              $('.page').width(document.body.clientWidth);
              $('.page').height(document.body.clientHeight);
			}
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
        $('.errorWin').modal();
    })
    //关闭弹框
    $('#closeWin').on('click',function(){
        $.modal.close()
    })


    //返回顶部
    var topDom = $("a.xl-backtop");
    var backDom = topDom.parents("div.backtop");
    function showDom(){
      if ($(document).scrollTop() > 0) {
        backDom.addClass("show-backtop");
      } else if ($(document).scrollTop() <= 0) {
        backDom.removeClass("show-backtop");
      }
    }
    showDom();
    $(window).scroll(function () {
    showDom();
    });

    topDom.on('click',function(){
      $('body,html').animate({scrollTop: 0}, 600);
      return false
    });

    //中奖名单 滚动
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
    var timer,i= 1,j=2;
    timer=setInterval(function(){
      scroll();
    },30);


  });
}).call(this);
