require.config
  paths:
    jquery: 'lib/jquery.min'
    'underscore':'lib/underscore-min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery', 'lib/countdown'], ($, countdown)->

  $('.container').on 'click', '.panel-p2p-product', ->
    url = $('.panel-title-bar a', $(this)).attr('href')
    window.location.href = url

  $('.p2pinfo-list-box').on('mouseenter',(e)->
    #console.log(e)
    target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id
    $('#'+target).show()
  ).on('mouseleave', (e)->
    target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id
    $('#'+target).hide()
  ).on('click',->
    url = $('.p2pinfo-title-content>a', $(this)).attr('href')
    window.location.href = url
  )

  # fetch cookie
  fetchCookie = (name) ->
    reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)")
    if arr = document.cookie.match(reg)
      return unescape(arr[2])
    else
      return null

  # set cookie
  # {number} day (cookie time)
  setCookie  = (key, value, day) ->
    date = new Date()
    date.setTime(date.getTime() + day * 24 * 60 * 60 * 1000);
    document.cookie = key + "=" + value+";expires="+date.toGMTString()
    console.log(document.cookie)

  #addEventListen close , set cookie
  $('.p2p-body-close').on('click', () ->
    $('.p2p-mask-warp').hide()
    setCookie('p2p_mask', 'show', 15);
  )

  # judge show or hide
  ((canShow)->

    if !canShow
      $('.p2p-mask-warp').show()

  )(fetchCookie('p2p_mask'))
