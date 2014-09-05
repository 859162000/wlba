require.config(
  paths:
    jquery: 'lib/jquery.min'
    "jquery.scroll.events": 'lib/jquery.scroll.events'

  shims:
    "jquery.scroll.events": ['jquery']
)

require ['jquery'], ($) ->
  $(document.body).bind 'scrollstart', () ->
    console.log('start')