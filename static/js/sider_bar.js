// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    $('#about-financing').mouseenter(function() {
      return $('.sidebar-secondary').show();
    });
    return $('#about-financing').mouseleave(function() {
      return $('.sidebar-secondary').hide();
    });
  });

}).call(this);

//# sourceMappingURL=sider_bar.map
