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
          $("div.sp-alt").show();
      });
      $("div.js-sp-close").on("click", function(){
          $(this).parents(".sp-alt").hide();
      });
  });
}).call(this);