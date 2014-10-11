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
  require(['jquery', 'underscore', 'lib/modal'], function($, _, modal) {});
  $('a[data-role=modal]').click(function(e) {
    e.preventDefault();
    return $(this).modal();
  });
}).call(this);
