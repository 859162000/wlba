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



  $('.container').on 'click', '.panel-p2p-product', ->
    url = $('.panel-title-bar a', $(this)).attr('href')
    window.location.href = url

  $('#topNotice').click (e) ->
        $('.common-inform').toggleClass('off')

  $('#p2p-new-announce').click (e)->
    e.stopPropagation()
    window.open($(this).attr('data-url'))

  $(document).ready ->
    setInterval (->
      $("#announce-title-scroll").find("ul:first").animate
        marginTop: "-25px"
      , 500, ->
        $(this).css(marginTop: "0px").find("li:first").appendTo this
        return
      return
    ), 3000
  return

