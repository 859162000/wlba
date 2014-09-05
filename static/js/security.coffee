require.config(
  paths:
    'jquery': 'lib/jquery.min'
    'jquery.scroll': 'lib/jquery.scroll'


  shim:
    'jquery.scroll': ['jquery']
)

require ['jquery', 'jquery.scroll'], ($, scroll) ->

  $(window).bind 'scrollstart', ->
    console.log('start')
    return

  $(window).bind 'scrollstop', ->
    console.log('stop')
    return
