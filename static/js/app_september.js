(function(){
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery'], function($) {
    //banner
    var winh = $(window).height();
    var banDom = $("#banner");
    banDom.height(winh);
    if(winh < 970){
      banDom.addClass("min-banner");
    }

    //close
    $("span.alert-close,a.alert-btn").click(function(){
      $(this).parents("div.alert-box").hide();
      $("div.alert-page").hide();
    });
    //领红包
    $("a.receive-red").click(function(){
      $("div.alert-page").show();
      $("div.alert-ok").show();
      //$("div.alert-error").show();
    });
  })
}).call(this);
