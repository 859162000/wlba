// Generated by CoffeeScript 1.8.0
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
    $('.container').on('click', '.panel-p2p-product', function() {
      var url;
      url = $('.panel-title-bar a', $(this)).attr('href');
      return window.location.href = url;
    });
    return $('.p2pinfo-list-box').on('mouseenter', function(e) {
      var target;
      target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id;
      return $('#' + target).show();
    }).on('mouseleave', function(e) {
      var target;
      target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id;
      return $('#' + target).hide();
    }).on('click', function() {
      var url;
      url = $('.p2pinfo-title-content>a', $(this)).attr('href');
      return window.location.href = url;
    });
  });

}).call(this);
