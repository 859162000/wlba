(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'jqueryRotate': 'jQueryRotate.2.2',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.modal': ['jquery'],
            'jquery.easing': ['jquery'],
            'jqueryRotate': ['jquery']
        }
    });
    require(['jquery'], function ($) {
        $("#click-prompt").click(function(){
            var dom = $("#click-info");
            if(dom.is(":hidden")){
              dom.stop(true,true).slideDown(200);
            }else{
              dom.stop(true,true).slideUp(200);
            }
        });
        //返回顶部
        function backTop(){
          $('body,html').animate({scrollTop: 0}, 600);
        }
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
    });
}).call(this);
