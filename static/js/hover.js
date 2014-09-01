// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function() {
    return $(document).ready(function() {
      return $('[data-role=hover]').each(function(index, elem) {
        $(elem).mouseenter(function(e) {
          var target;
          e.preventDefault();
          target = $(e.target).attr('data-target');
          return $(target).show();
        });
        return $(elem).mouseleave(function(e) {
          var target;
          e.preventDefault();
          target = $(e.target).attr('data-target');
          return $(target).hide();
        });
      });
    });
  });

}).call(this);
