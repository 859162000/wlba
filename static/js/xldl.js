
// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.complexify': 'lib/jquery.complexify.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      'underscore': 'lib/underscore-min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.validate': ['jquery'],
      'jquery.complexify': ['jquery'],
      'jquery.placeholder': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', "tools", 'jquery.complexify', 'jquery.placeholder', 'underscore'], function($, modal, backend, validate, tool, complexify, placeholder, _) {
    var checkMobile, container, csrfSafeMethod, getCookie, msg_count, sameOrigin, _showModal;
    myeven();
    function myeven() {
      var high = document.body.scrollHeight;
      $('#top-zc').on('click', function () {
        pageScroll();
      });

      function pageScroll() {
        //把内容滚动指定的像素数
        window.scrollBy(0, -high);
        //获取scrollTop值
        var sTop = document.documentElement.scrollTop + document.body.scrollTop;
        //判断当页面到达顶部
        if (sTop == 0) clearTimeout(scrolldelay);
      }

      //文本框的得到和失去光标
      var zhi;
      $('.com-tu').on("focus", function () {
        if ($(this).attr('placeholder')) {
          zhi = $(this).attr('placeholder');
        }
        $(this).attr('placeholder', '');
      });

      $('.com-tu').on('blur', function () {
        $(this).attr('placeholder', zhi)
      })

      $('#button-get-validate-code-modal').on('click', function () {
        $(this).disabled = false;
        setTimeout(function () {
          $('#button-get-validate-code-modal').disabled = true;
          $('.show').removeClass('hidden');
        }, 60000)
      });
    }

  });

}).call(this);

//# sourceMappingURL=login_modal.js.map

