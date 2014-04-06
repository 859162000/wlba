require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend', 'lib/calculator'], ($, backend)->
  $('#addToFavorite').click (e)->
    backend.addToFavorite e, 'funds'
