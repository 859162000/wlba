(function(){
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery'], function($) {
    //banner
    var banDom = $("#banner");
    var winh = $(window).height();
    banDom.height(winh);
    if(winh < 970){
        banDom.addClass("min-banner");
    }

    var ipad = navigator.userAgent.match(/(iPad).*OS\s([\d_]+)/) ? true : false,
        iphone = !ipad && navigator.userAgent.match(/(iPhone\sOS)\s([\d_]+)/) ? true : false,
        ios = ipad || iphone;
    if (ios) {
      document.getElementById('ios-show').style.display = 'block';
    }
})
}).call(this);
