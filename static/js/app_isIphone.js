(function(){
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery'], function($) {
    var ipad = navigator.userAgent.match(/(iPad).*OS\s([\d_]+)/) ? true : false,
        iphone = !ipad && navigator.userAgent.match(/(iPhone\sOS)\s([\d_]+)/) ? true : false,
        ios = ipad || iphone;
    if (ios) {
      document.getElementById('ios-show').style.display = 'block';
    }
})
}).call(this);