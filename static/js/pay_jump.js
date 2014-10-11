(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery'], function($) {
    return $('#huifu-pay').submit();
  });
}).call(this);
