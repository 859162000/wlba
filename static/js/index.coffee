require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'

require ['jquery', 'underscore'], ($, _)->

  # setup tab logics
  $('ul.tabs').each ()->

    allAnchors = $(this).find('a.tab-anchor')

    allTargets = allAnchors
    .map ()->
      $(this).attr('data-toggle')


    $(this).find('a.tab-anchor').each ->
      $(this).click (e)->
        e.preventDefault()

        targetId = $(this).attr('data-toggle')

        $(allAnchors).each ->
          $(this).removeClass 'active'

        $(allTargets).each ->
          if this != targetId
            $('#'+this).hide()

        $('#'+targetId).fadeIn()
        $(this).addClass 'active'
        $('.tab-arrow').remove()
        $($(this).parent()).append("<img class='tab-arrow' src='/static/images/red-arrow.png'/>")
    .each (index)->
      if index == 0
        $(this).trigger('click')

  $('.portfolio-submit').click ()->
    asset = $('#portfolio-asset')[0].value
    period = $('#portfolio-period')[0].value
    risk = $('#portfolio-risk')[0].value
    window.location.href = '/portfolio/?period=' + period + '&asset=' + asset + '&risk=' + risk

  $('.portfolio-input').keyup (e)->
    if e.keyCode == 13
      $('.portfolio-submit').click()

  currentBanner = 0
  banners = $('*[class^="home-banner"]')
  anchors = $('.background-anchor')
  setInterval(()->
      $(banners[currentBanner]).hide()
      $(anchors[currentBanner]).toggleClass('active')
      currentBanner = (currentBanner + 1) % banners.length
      $(banners[currentBanner]).fadeIn()
      $(anchors[currentBanner]).toggleClass('active')
    , 6000)

  $('.background-anchor').click (e)->
    e.preventDefault()
    index = $(e.target).parent().index()
    if(index != currentBanner)
      $(banners[currentBanner]).hide()
      $(anchors[currentBanner]).toggleClass('active')
      $(banners[index]).fadeIn()
      $(anchors[index]).toggleClass('active')
      currentBanner = index

  $('.home-banner-2').click ()->
    window.location.href='/trust/detail/8526'

