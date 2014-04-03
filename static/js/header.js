// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery', 'lib/backend'], function($, backend) {
    var previous;
    previous = $('.category-anchor')[0];
    $('.category-anchor').click(function(e) {
      e.preventDefault();
      $(previous).removeClass('active');
      $(e.target).addClass('active');
      return previous = e.target;
    });
    $('.header-button').click(function() {
      var period, type, uri;
      period = $('.header-select')[0].value;
      type = $(previous).attr('data-type');
      uri = '/' + type;
      if (type === 'cash') {
        uri += '/home/';
      } else {
        uri += '/products/';
      }
      return window.location.href = uri + '?period=' + period + '&asset=' + $('.header-asset')[0].value;
    });
    return $('.header-input-base').keyup(function(e) {
      if (e.keyCode === 13) {
        return $('.header-button').click();
      }
    });
  });

}).call(this);

//# sourceMappingURL=header.map
