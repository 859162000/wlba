/**
 * Created by rsj217 on 15-1-21.
 */
// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      'jquery': 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    if($('.success-icon').length==1){
        var tm=$('#tm').text();
        var tm_timer=setInterval(function(){
          $('#tm').html(tm--);
          if(tm==-1){
            window.location.href='/p2p/list/';
          }
        },1000)
    }
  });
}).call(this);
