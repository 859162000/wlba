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
              $('.page,.errorWin').show();
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

    function closeAlert(tp){//关闭弹层
      tp.hide();
      $('.page').hide();
    }
    function backTop(){
      $('body,html').animate({scrollTop: 0}, 600);
    }
    //关闭 抽奖 遮罩\弹框
    $('.spanBtn,.againBtn').on('click',function(){
      closeAlert($(this).parents("div.alert-box"))
    });
    //非法用户
    $('#checkUserStatus').on('click',function(){
        $('.errorWin').modal();
    });


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
      backTop();
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

    //返回banner处
    $(".to-register").on("click",function(){
      $('.page,.promote-register').show();
    });
    //返回banner处
    $("a.banner-register").on("click",function(){
      closeAlert($(this).parents(".alert-box"));
      backTop();
    });
    //立即注册 btn
    $(".now-register").on("click",function(){
      backTop();
    });
  });

  (function(){
    //中奖名单
    $.ajax({
      type: "post",
      url: "/api/award/common_september/",
      dataType: "json",
      data: {action: "GET_AWARD"},
      success: function(data){
        console.log(data,"中奖名单");
      }
    });

    //是不是合法用户
    $.ajax({
      type: "post",
      url: "/api/award/common_september/",
      dataType: "json",
      data: {action: "IS_VALID"},
      success: function(data){
        console.log(data);
      }
    });

  })();

}).call(this);
