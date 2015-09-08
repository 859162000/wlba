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
    //立即参与
    $('.btn').on('click',function(){
      var re_top=$('.erweima').offset().top;
      $('body,html').animate({scrollTop:re_top}, 600);
      return false
    })
  });

}).call(this);



