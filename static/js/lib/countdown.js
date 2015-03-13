// Generated by CoffeeScript 1.8.0
(function() {
  define(['jquery', 'underscore'], function($, _) {
    var countdown, counters, loadTime, twoDigit;
    loadTime = new Date().getTime();
    counters = $('*[data-role=countdown]');
    twoDigit = function(n) {
      if (n < 10) {
        return '0' + n;
      }
      return '' + n;
    };
    countdown = function() {
      var diffInSeconds, now;
      now = new Date().getTime();
      diffInSeconds = (now - loadTime) / 1000;
      return _.each(counters, function(e) {
        var components, day, left, seconds, timeString;
        left = $(e).attr('data-left');
        components = left.split(":");
        seconds = parseInt(components[0]) * 3600 + parseInt(components[1]) * 60 + parseInt(components[2]);
        if (seconds > 0) {
          left = seconds - diffInSeconds;
          if (left > 0) {
            timeString = "";
            day = Math.floor(left / 86400);
            if (day > 0) {
              timeString += day + "天";
              left = Math.floor(left % 86400);
            }
            timeString += Math.floor(left / 3600) + "小时" + twoDigit(Math.floor(left % 3600 / 60)) + "分" + twoDigit(Math.floor(left % 60)) + "秒";
            return $($(e).attr('data-target')).text(timeString);
          }
        }
      });
    };
    return setInterval(countdown, 1000);
  });

}).call(this);

//# sourceMappingURL=countdown.js.map
