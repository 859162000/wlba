// Generated by CoffeeScript 1.9.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function() {
    return $(document).ready(function() {
      $('[data-role=hover]').bind('mouseenter', function(e) {
        var target;
        e.preventDefault();
        target = $(e.target).attr('data-target');
        return $(target).show();
      }).bind('mouseleave', function(e) {
        var target;
        e.preventDefault();
        target = $(e.target).attr('data-target');
        return $(target).hide();
      });
      $('[data-name=hoverbox]').bind('mouseenter', function(e) {
        return $(this).show();
      }).bind('mouseleave', function(e) {
        return $(this).hide();
      });
      $('.mobile-app-top').bind('mouseenter', function(e) {
        return $('.mobile-app-top-prompt').show();
      }).bind('mouseleave', function(e) {
        return $('.mobile-app-top-prompt').hide();
      });
      $('.mobile-app-top-prompt').bind('mouseenter', function(e) {
        return $(this).show();
      }).bind('mouseleave', function(e) {
        return $(this).hide();
      });
      $('.mobile-app-bottom').bind('mouseenter', function(e) {
        return $('.mobile-app-bottom-prompt').show();
      }).bind('mouseleave', function(e) {
        return $('.mobile-app-bottom-prompt').hide();
      });
      $('.mobile-app-bottom-prompt').bind('mouseenter', function(e) {
        return $(this).show();
      }).bind('mouseleave', function(e) {
        return $(this).hide();
      });
      $('#sidebar-second').bind('mouseenter', function(e) {
        if ($('.sidebar-secondary').attr('style') !== 'display:block') {
          return $('.sidebar-secondary').slideDown();
        }
      });
      return $('.sidebar-secondary').bind('mouseenter', function(e) {
        return $(this).show();
      }).bind('mouseleave', function(e) {
        if ($('.sidebar-secondary').attr('style') !== 'display:block') {
          return $(this).slideUp();
        }
      });
    });
  });

}).call(this);
