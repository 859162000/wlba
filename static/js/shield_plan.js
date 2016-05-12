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
      $("a.js-file").on("click", function(){
        $("div.sp-alt").css("display", "-webkit-box");
      });
      $("div.sp-alt").on("click", function(){
         $(this).hide();
      });
  });
}).call(this);