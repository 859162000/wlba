require.config
  paths:
    jquery: 'lib/jquery.min'
    iealert: 'lib/iealert.min'
  shim:
    'iealert': ['jquery']

require ['jquery', 'lib/backend', 'iealert'], ($, backend, iealert)->
  $(document).ready ()->
    $("body").iealert({
      title: "您使用的IE浏览器版本过低",
      text: '为了获得更好的浏览体验，请点击下面的按钮升级您的浏览器',
      upgradeTitle: '立即升级',
      support: 'ie7',
      closeBtn: false
    })

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
    window.location.href= uri + '?period=' + period + '&asset=' + $('.header-asset-input')[0].value

  $('.header-input-base').keyup (e)->
    if e.keyCode == 13
      $('.header-button').click()


  $('.user-center').mouseenter ()->
    $('#user-items').css('display', 'block')
    $('#username').toggleClass('username-hover')

  $('.user-center').mouseleave ()->
    $('#user-items').css('display', 'none')
    $('#username').toggleClass('username-hover')
