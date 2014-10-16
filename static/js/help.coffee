require.config(
  paths:
    'jquery': 'lib/jquery.min'
)

require ['jquery'], ($) ->
  $('.list-item-title').on 'click', () ->

