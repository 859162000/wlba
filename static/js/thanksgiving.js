 (function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery'], function($) {
      //固定回到顶部
            function backtop() {
                var k = document.body.clientWidth,
                        a = k - 100
                return a;
            }

            var left2 = backtop();
            //浏览器大小改变触发的事件
            window.onresize = function () {
                left2 = backtop();
            };
            //赋值
            $('.xl-backtop').css({'left': left2});
            //显示微信二维码
            $('#xl-weixin').on('mouseover', function () {
                $('.erweima').show();
            });
            $('#xl-weixin').on('mouseout', function () {
                $('.erweima').hide();
            })
            //返回顶部
            $(window).scroll(function () {
                if ($(document).scrollTop() > 0) {
                    $(".xl-backtop").fadeIn();
                } else {
                    $('.xl-backtop').stop().fadeOut();
                }
            });
            $('.backtop').on('click', function () {
                $('body,html').animate({scrollTop: 0}, 600);
                return false
            })

  });

}).call(this);