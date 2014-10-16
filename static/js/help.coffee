require.config(
  paths:
    'jquery': 'lib/jquery.min'
)

require ['jquery'], ($) ->
  $('.list-item-title').on 'click', '.list-item-title', (e) ->
    console.log('hello, world')

