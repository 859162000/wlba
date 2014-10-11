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
    var anchors, bannerCount, banners, currentBanner, switchBanner, timer;
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
    return $('#topNotice').click(function(e) {
      return $('.common-inform').toggleClass('off');
    });
  });
}).call(this);
