(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery'], function($) {
    var countDown, inter, t;
    t = 5;
    countDown = function() {
      var timeSpan;
      timeSpan = $('#count_down');
      t--;
      $('#count_down').html(t);
      if (t <= 0) {
        location.href = "/";
        return clearInterval(inter);
      }
    };
    return inter = setInterval(countDown, 1000);
  });
}).call(this);
