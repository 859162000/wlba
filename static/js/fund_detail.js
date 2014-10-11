(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });
  require(['jquery', 'lib/backend', 'lib/calculator'], function($, backend) {
    $('#addToFavorite').click(function(e) {
      return backend.addToFavorite(e.target, 'funds');
    });
    return $('input[data-role=earning-calculator]').trigger('keyup');
  });
}).call(this);
