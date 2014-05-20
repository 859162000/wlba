require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend', 'lib/calculator'], ($, backend)->
  $('#addToFavorite').click (e)->
    backend.addToFavorite e.target, 'funds'

  $('input[data-role=earning-calculator]').trigger('keyup')
