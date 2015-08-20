require.config({
  paths: {
    'jquery.fullPage': 'lib/jquery.fullPage.min',
  },
  shim: {
    'jquery.fullPage': ['jquery'],
  }
});

require(['jquery', 'jquery.fullPage'], function( $ ) {
  var page_h = $(window).height()
  $('.section').height(page_h);

  $(document).ready(function() {
    $('#fullpage').fullpage({
      anchors: ['Page1', 'Page2', 'Page3', 'Page4', 'Page5', 'Page6'],
			menu: '#menu',
      scrollingSpeed: 500
    });
  });
});