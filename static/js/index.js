// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min'
    }
  });

  require(['jquery', 'underscore'], function($, _) {
    var anchors, banners, currentBanner;
    $('ul.tabs').each(function() {
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
          $(this).addClass('active');
          $('.tab-arrow').remove();
          return $($(this).parent()).append("<img class='tab-arrow' src='/static/images/red-arrow.png'/>");
        });
      }).each(function(index) {
        if (index === 0) {
          return $(this).trigger('click');
        }
      });
    });
    $('.portfolio-submit').click(function() {
      var asset, period, risk;
      asset = $('#portfolio-asset')[0].value;
      period = $('#portfolio-period')[0].value;
      risk = $('#portfolio-risk')[0].value;
      return window.location.href = '/portfolio/?period=' + period + '&asset=' + asset + '&risk=' + risk;
    });
    $('.portfolio-input').keyup(function(e) {
      if (e.keyCode === 13) {
        return $('.portfolio-submit').click();
      }
    });
    currentBanner = 0;
    banners = $('*[class^="home-banner"]');
    anchors = $('.background-anchor');
    setInterval(function() {
      $(banners[currentBanner]).hide();
      $(anchors[currentBanner]).toggleClass('active');
      currentBanner = (currentBanner + 1) % 3;
      $(banners[currentBanner]).fadeIn();
      return $(anchors[currentBanner]).toggleClass('active');
    }, 6000);
    $('.background-anchor').click(function(e) {
      var index;
      e.preventDefault();
      index = $(e.target).parent().index();
      if (index !== currentBanner) {
        $(banners[currentBanner]).hide();
        $(anchors[currentBanner]).toggleClass('active');
        $(banners[index]).fadeIn();
        $(anchors[index]).toggleClass('active');
        return currentBanner = index;
      }
    });
    return $('.home-banner-2').click(function() {
      return window.location.href = '/trust/detail/8526';
    });
  });

}).call(this);

//# sourceMappingURL=index.map
