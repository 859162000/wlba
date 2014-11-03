// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      'jquery': 'lib/jquery.min',
      'jquery.scroll': 'lib/jquery.scroll',
      'security_effect': 'security_effect'
    },
    shim: {
      'jquery.scroll': ['jquery'],
      'security_effect': ['jquery'],
      'autofloat': ['jquery']
    }
  });

  require(['jquery', 'jquery.scroll', 'security_effect'], function($, scroll, effect) {
    $(window).load(function() {
      $.effect.dispatch();
    });
    $(window).bind('scroll', function() {
      $.effect.setTabBar();
    });
    $(window).bind('scrollstop', function() {
      $.effect.dispatch();
    });
    $('.security-bar').on('click', 'a', function(e) {
      var t;
      $('.security-bar a').removeClass('active');
      $(this).addClass('active');
      t = $($(this).attr('href')).offset().top;
      return $(window).scrollTop(t);
    });
    return $('.animation_02,.animation_13,.animation_03').mouseover(function() {
      var image;
      image = $('img', $(this));
      return image.bounceIn();
    });
  });

}).call(this);
