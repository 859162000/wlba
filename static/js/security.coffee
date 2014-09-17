require.config(
  paths:
    'jquery': 'lib/jquery.min'
    'jquery.scroll': 'lib/jquery.scroll'
    'security_effect': 'security_effect'


  shim:
    'jquery.scroll': ['jquery']
    'security_effect': ['jquery']
    'autofloat': ['jquery']

)

require ['jquery', 'jquery.scroll', 'security_effect'], ($, scroll, effect) ->

  $(window).load  ->
    $.effect.dispatch()
    return

  $(window).bind 'scroll', ->
    $.effect.setTabBar()
    return

  $(window).bind 'scrollstop', ->
    $.effect.dispatch()
    return

  $('.security-bar').on 'click', 'a', (e) ->
    $('.security-bar a').removeClass('active')
    $(this).addClass('active')

  #mouseover
  $('.animation_02,.animation_13,.animation_03').mouseover ->
    image = $('img', $(this))
    image.bounceIn()

