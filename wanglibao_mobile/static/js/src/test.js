require.config({
    baseUrl: '/static/js',
    paths: {
      'jquery': 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'underscore': 'lib/underscore-min'
    },
    shim: {
      'jquery.modal': ['underscore','jquery']
    }
});

require(['jquery.modal'], function(modal) {
    console.log($.trim('hetao - '), 'hh')
});
