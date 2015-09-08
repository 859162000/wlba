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
    var H=window.innerHeight/2-$('.erweima').height()
    $('.btn').on('click',function(){
      var re_top=$('.erweima').offset().top;
      $('body,html').animate({scrollTop:re_top+H}, 600);
      return false
    })
  });

}).call(this);



