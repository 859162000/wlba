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
      return $('[data-name=hoverbox]').bind('mouseenter', function(e) {
        return $(this).show();
      }).bind('mouseleave', function(e) {
        return $(this).hide();
      });
    });
  });
}).call(this);
