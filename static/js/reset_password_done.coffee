require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ($)->
  t = 5
  countDown = ()->
    timeSpan = $('#count_down')
    t--
    $('#count_down').html(t)
    if t <= 0
      location.href = "/"
      clearInterval(inter)
  inter = setInterval countDown, 1000