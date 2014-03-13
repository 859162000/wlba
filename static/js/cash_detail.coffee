require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $ document
  .ready ->
    $('#addToFavorite').click (e)->
      e.preventDefault()

      id = $(e.target).attr('data-id')
      backend.addToFavorite 'cashes', id
