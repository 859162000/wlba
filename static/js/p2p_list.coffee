require.config
  paths:
    jquery: 'lib/jquery.min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery'], ($)->

  $('.container').on 'click', '.panel-p2p-product', ->
    url = $('.panel-title-bar a', $(this)).attr('href')
    window.location.href = url

  $('.p2pinfo-list-box').on('mouseenter',(e)->
    target = e.currentTarget.lastElementChild.id
    #console.log(target)
    $('#'+target).fadeIn()
  ).on('mouseleave', (e)->
    target = e.currentTarget.lastElementChild.id
    $('#'+target).fadeOut()
  ).on('click',->
    url = $('.p2pinfo-title-content>a', $(this)).attr('href')
    window.location.href = url
  )