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

  tops = () ->
    tabs = ['day', 'week', 'month']
    index = 0
    topTimer = null
    timeStep = 4000

    topsFunc =
      switchTab: (tabIndex) ->
        id = (if $.isNumeric(tabIndex) then '#'+tabs[tabIndex] else tabIndex)
        $('.tabs a').removeClass('active')
        $('.tabs-nav a[href="' + id + '"]').addClass('active')

        $('.tab-content').hide()
        $(id).show()

        index = (if $.isNumeric(tabIndex) then tabIndex else tabs.indexOf(tabIndex))

      nextTab: () ->
        if index == tabs.length - 1
          index = 0
          return index

        return ++index

      setIndex: (tabIndex) ->
        index = tabIndex

      getIndex: () ->
        return index

      startScroll: () ->
        topTimer = setTimeout(topsFunc.scrollTab, timeStep)

      stopScroll: (id) ->
        topsFunc.setIndex(tabs.indexOf(id.split('#')[1]))
        clearTimeout(topTimer)

      scrollTab: () ->
        topsFunc.switchTab(topsFunc.nextTab())
        topTimer = setTimeout(topsFunc.scrollTab, timeStep)

    return topsFunc

  $(document).ready ->
    setInterval (->
      $("#announce-title-scroll").find("ul:first").animate
        marginTop: "-25px"
      , 500, ->
        $(this).css(marginTop: "0px").find("li:first").appendTo this
        return
      return
    ), 3000

    tops = tops()

    tops.switchTab(0)
    tops.startScroll()

    $('.tabs a').mouseenter (e) ->
      tops.stopScroll($(this).attr('href'))
      tops.switchTab($(this).attr('href'))

    $('.tabs a').mouseleave (e) ->
      tops.startScroll()

    $('.tabs a').click (e) ->
      e.preventDefault()

    $('.panel-title-bar__tops').click (e) ->
      location.href = '/activity/newyear'
  return

