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

