require.config({
  paths: {
    'jquery.fullPage': 'lib/jquery.fullPage.min',
    'videojs': 'lib/video.min',

  },
  shim: {
    'jquery.fullPage': ['jquery'],
  }
});

require(['jquery', 'videojs'], function( $ ,videojs) {
  var player = videojs('really-cool-video', { /* Options */ }, function() {
    console.log('Good to go!');
    //this.play();

  });

});