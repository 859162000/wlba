require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ($)->
  $('#about-financing').mouseenter ()->
    $('.sidebar-secondary').show()
  $('#about-financing').mouseleave ()->
    $('.sidebar-secondary').hide()
