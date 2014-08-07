require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    'jquery.modal': 'lib/jquery.modal.min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery', 'underscore', 'lib/backend', 'lib/modal', 'lib/countdown'], ($, _, backend, modal, countdown)->
  $('.portfolio-submit').click ()->
    asset = $('#portfolio-asset')[0].value
    period = $('#portfolio-period')[0].value
    window.location.href = '/portfolio/?period=' + period + '&asset=' + asset

  $('.portfolio-input').keyup (e)->
    if e.keyCode == 13
      $('.portfolio-submit').click()

  currentBanner = 0
  banners = $('*[class^="home-banner"]')
  bannerCount = banners.length
  anchors = $('.background-anchor')

  switchBanner = ()->
    $(banners[currentBanner]).hide()
    $(anchors[currentBanner]).toggleClass('active')
    currentBanner = (currentBanner + 1) % bannerCount
    $(banners[currentBanner]).fadeIn()
    $(anchors[currentBanner]).toggleClass('active')

  timer = setInterval(switchBanner, 6000)

  $('.background-anchor').mouseover (e)->
    clearInterval(timer)

  $('.background-anchor').mouseout (e)->
    timer = setInterval(switchBanner, 6000)

  $('.background-anchor').click (e)->
    e.preventDefault()
    index = $(e.target).parent().index()
    if(index != currentBanner)
      $(banners[currentBanner]).hide()
      $(anchors[currentBanner]).toggleClass('active')
      $(banners[index]).fadeIn()
      $(anchors[index]).toggleClass('active')
      currentBanner = index
