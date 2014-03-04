// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    return $(document).ready(function() {
      var switchBackground, switchBackgroundWrapper;
      switchBackground = function(max) {
        var current, imageUrl, matches;
        imageUrl = $('.big-background').css('background-image');
        matches = imageUrl.match(/\/bg(\d).jpg/);
        if (matches.length === 2) {
          current = parseInt(matches[1]) + 1;
          if (current > max) {
            current = 1;
          }
          return $('.big-background').css('background-image', imageUrl.replace(/\/bg\d.jpg/, '/bg' + current + '.jpg'));
        }
      };
      switchBackgroundWrapper = function() {
        switchBackground(4);
        return setTimeout(switchBackgroundWrapper, 10 * 1000);
      };
      setTimeout(switchBackgroundWrapper, 10 * 1000);
      return $('ul.tabs').each(function() {
        var allAnchors, allTargets;
        allAnchors = $(this).find('a.tab-anchor');
        allTargets = allAnchors.map(function() {
          return $(this).attr('data-toggle');
        });
        return $(this).find('a.tab-anchor').each(function() {
          return $(this).click(function(e) {
            var targetId;
            e.preventDefault();
            targetId = $(this).attr('data-toggle');
            $(allAnchors).each(function() {
              return $(this).removeClass('active');
            });
            $(allTargets).each(function() {
              if (this !== targetId) {
                return $('#' + this).hide();
              }
            });
            $('#' + targetId).fadeIn();
            return $(this).addClass('active');
          });
        }).each(function(index) {
          if (index === 0) {
            return $(this).trigger('click');
          }
        });
      });
    });
  });

}).call(this);

//# sourceMappingURL=index.map
