require.config(
  paths:
    'jquery': 'lib/jquery.min'
    'jquery.scroll': 'lib/jquery.scroll'
    'security_effect': 'security_effect'
    'autofloat': 'lib/autofloat'


  shim:
    'jquery.scroll': ['jquery']
    'security_effect': ['jquery']
    'autofloat': ['jquery']


)

require ['jquery', 'jquery.scroll', 'security_effect', 'autofloat'], ($, scroll, effect, autofloat) ->

  util =
    getDistanceFromBottom: (ele) ->
      wheight = $(window).height()
      distance = ele.offset().top - $(window).scrollTop()
      return wheight - distance

    orders: 0

    pipeflow: () ->
      step = 5
      pwidth = 820
      mheight = 108
      pheight = 170
      speed = 50

      pipeline = $('.pipeline_01 .pipeline')

      mtds = [
        ->
          currenth = pipeline.height() + step
          pipeline.height(currenth)
          if pipeline.height() >= mheight
            util.orders++
          setTimeout util.pipeflow, speed
        ->
          currentw = pipeline.width() + step
          pipeline.width(currentw)
          if pipeline.width() >= pwidth
            util.orders++
          setTimeout util.pipeflow, speed
        ->
          currenth = pipeline.height() + step
          pipeline.height(currenth)
          if pipeline.height() < pheight
            setTimeout util.pipeflow, speed
      ]

      mtds[util.orders].call(this)
      return

  events =
    item_01:
      distance: 200
      name: '机构筛选'
      selector: '.organization'
      animate: () ->
        $('.guarantee-list-item', $('.organization')).addClass('fadeInUp')
        return
    item_02:
      distance: 50
      name: '机构筛选'
      selector: '.pipeline_01'
      animate: () ->
        util.pipeflow()
        return


  $(window).load  ->
    $(window).trigger('scrollstop')
    return

  $(window).bind 'scroll', ->
    $.effect.setTabBar()
    return

  $(window).bind 'scrollstop', ->
    $.effect.dispatch()
    return

  $('.security-bar').on 'click', 'a', (e) ->
    e.preventDefault()
    $('.security-bar a').removeClass('active')
    $(this).addClass('active')
    id = $(this).attr('href').replace('#', '')
    $('.security-panel').each( (index, item) ->
      if $(item).attr('id') == id
        if $(item).hasClass('hidden')
          $(item).removeClass('hidden')
      else
        if !$(item).hasClass('hidden')
          $(item).addClass('hidden')
    )

    $().removeClass('hidden')