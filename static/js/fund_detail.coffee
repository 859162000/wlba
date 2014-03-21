require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $('#addToFavorite').click (e)->
    backend.addToFavorite e, 'funds'
