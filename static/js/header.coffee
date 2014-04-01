require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  previous = $('.category-anchor')[0]
  $('.category-anchor').click (e)->
    e.preventDefault()
    $(previous).removeClass('active')
    $(e.target).addClass('active')
    previous = e.target


  $('.header-button').click ()->
    period = $('.header-select')[0].value
    type = $(previous).attr('data-type')
    uri = '/' + type
    if type == 'cash'
      uri += '/home/'
    else
      uri += '/products/'
    window.location.href= uri + '?period=' + period