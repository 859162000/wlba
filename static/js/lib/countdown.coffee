define ['jquery', 'underscore'], ($, _)->
  loadTime = Date.now()

  counters = $('*[data-role=countdown]')

  twoDigit = (n)->
    if n < 10
      return '0' + n
    return '' + n

  countdown = ()->
    now = Date.now()

    diffInSeconds = (now - loadTime)/ 1000
    _.each counters, (e)->
      left = $(e).attr 'data-left'
      components = left.split(":")
      seconds = parseInt(components[0]) * 3600 + parseInt(components[1]) * 60 + parseInt(components[2])

      if seconds > 0
        left = seconds - diffInSeconds

        timeString = Math.floor(left / 3600) + ":" + twoDigit(Math.floor(left % 3600 / 60)) + ":" + twoDigit(Math.floor(left % 60))

        $($(e).attr 'data-target').text timeString

  setInterval(countdown, 1000)
