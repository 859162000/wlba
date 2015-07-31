
require.config({
  paths: {
    'jquery.animateNumber': 'lib/jquery.animateNumber.min'
  },
  shim: {
    'jquery.animateNumber': ['jquery']
  }
});

require(['jquery', 'jquery.animateNumber'], function( $ ) {
    $('.num-animate').prop('number', 0).animateNumber({
      number: 5000,
    },2000);
});