require.config
  paths:
    jquery: 'lib/jquery.min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery'], ($)->

  $('.container').on 'click', '.panel-p2p-product', ->
    url = $('.panel-title-bar a', $(this)).attr('href')
    window.location.href = url

  $('.p2pinfo-list-box').bind('mouseenter',(e)->
    target = e.currentTarget.lastElementChild.id
    #console.log(target)
    $('#'+target).show()
  ).bind('mouseleave', (e)->
    target = e.currentTarget.lastElementChild.id
    $('#'+target).hide()
  )