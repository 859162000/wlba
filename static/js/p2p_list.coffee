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