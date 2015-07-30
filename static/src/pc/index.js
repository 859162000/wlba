
require.config({
  paths: {
    'jquery.placeholder': 'lib/jquery.placeholder'
  },
  shim: {
    'jquery.placeholder': ['jquery']
  }
});

require(['jquery', 'jquery.placeholder'], function( $ ) {
   $('input, textarea').placeholder();
});