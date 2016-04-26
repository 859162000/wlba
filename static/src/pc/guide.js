require.config({
  paths: {
    'videojs': 'lib/video.min'

  }
});

require(['jquery', 'videojs'], function( $ ,videojs) {
  var player = videojs('really-cool-video', { /* Options */ }, function() {
    console.log('Good to go!');
    //this.play();

  });

});