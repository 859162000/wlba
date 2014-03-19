require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $('#addToFavorite').click (e)->
    e.preventDefault()

    id = $(e.target).attr('data-id')
    backend.addToFavorite 'funds', id
