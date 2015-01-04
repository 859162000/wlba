// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      'jquery.modal': 'lib/jquery.modal.min'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery', 'underscore', 'lib/backend', 'lib/modal', 'lib/countdown'], function($, _, backend, modal, countdown) {
    var anchors, bannerCount, banners, currentBanner, switchBanner, timer, tops;
    $('.portfolio-submit').click(function() {
      var asset, period;
      asset = $('#portfolio-asset')[0].value;
      period = $('#portfolio-period')[0].value;
      return window.location.href = '/portfolio/?period=' + period + '&asset=' + asset;
    });
    $('.portfolio-input').keyup(function(e) {
      if (e.keyCode === 13) {
        return $('.portfolio-submit').click();
      }
    });
    currentBanner = 0;
    banners = $('*[class^="home-banner"]');
    bannerCount = banners.length;
    anchors = $('.background-anchor');
    switchBanner = function() {
      $(banners[currentBanner]).hide();
      $(anchors[currentBanner]).toggleClass('active');
      currentBanner = (currentBanner + 1) % bannerCount;
      $(banners[currentBanner]).fadeIn();
      return $(anchors[currentBanner]).toggleClass('active');
    };
    timer = setInterval(switchBanner, 6000);
    $('.background-anchor').mouseover(function(e) {
      return clearInterval(timer);
    });
    $('.background-anchor').mouseout(function(e) {
      return timer = setInterval(switchBanner, 6000);
    });
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
    $('.container').on('click', '.panel-p2p-product', function() {
      var url;
      url = $('.panel-title-bar a', $(this)).attr('href');
      return window.location.href = url;
    });
    $('#topNotice').click(function(e) {
      return $('.common-inform').toggleClass('off');
    });
    $('#p2p-new-announce').click(function(e) {
      e.stopPropagation();
      return window.open($(this).attr('data-url'));
    });
    tops = function() {
      var index, tabs, timeStep, topTimer, topsFunc;
      tabs = ['day', 'week', 'month'];
      index = 0;
      topTimer = null;
      timeStep = 4000;
      topsFunc = {
        switchTab: function(tabIndex) {
          var id;
          id = ($.isNumeric(tabIndex) ? '#' + tabs[tabIndex] : tabIndex);
          $('.tabs a').removeClass('active');
          $('.tabs-nav a[href="' + id + '"]').addClass('active');
          $('.tab-content').hide();
          $(id).show();
          return index = ($.isNumeric(tabIndex) ? tabIndex : tabs.indexOf(tabIndex));
        },
        nextTab: function() {
          if (index === tabs.length - 1) {
            index = 0;
            return index;
          }
          return ++index;
        },
        setIndex: function(tabIndex) {
          return index = tabIndex;
        },
        getIndex: function() {
          return index;
        },
        startScroll: function() {
          return topTimer = setTimeout(topsFunc.scrollTab, timeStep);
        },
        stopScroll: function(id) {
          topsFunc.setIndex(tabs.indexOf(id.split('#')[1]));
          return clearTimeout(topTimer);
        },
        scrollTab: function() {
          topsFunc.switchTab(topsFunc.nextTab());
          return topTimer = setTimeout(topsFunc.scrollTab, timeStep);
        }
      };
      return topsFunc;
    };
    $(document).ready(function() {
      setInterval((function() {
        $("#announce-title-scroll").find("ul:first").animate({
          marginTop: "-25px"
        }, 500, function() {
          $(this).css({
            marginTop: "0px"
          }).find("li:first").appendTo(this);
        });
      }), 3000);
      tops = tops();
      tops.switchTab(0);
      tops.startScroll();
      $('.tabs a').mouseenter(function(e) {
        tops.stopScroll($(this).attr('href'));
        return tops.switchTab($(this).attr('href'));
      });
      $('.tabs a').mouseleave(function(e) {
        return tops.startScroll();
      });
      return $('.tabs a').click(function(e) {
        return e.preventDefault();
      });
    });
  });

}).call(this);

//# sourceMappingURL=index.map
