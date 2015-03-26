require.config({
    baseUrl: '/static/js',
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
    },
    shim: {
      'jquery.modal': ['jquery']
    }
});

require(['jquery', 'jquery.modal'], function($, modal) {
    console.log($.trim('hetao - '), 'hh')
});
