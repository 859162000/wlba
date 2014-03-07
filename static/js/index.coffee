require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'

require ['jquery', 'underscore'], ($, _)->
  $(document).ready ->

    # setup the background switcher
    switchBackground = ->
      backgrounds = $('.big-background')
      current = _.find backgrounds, (value)->
        $(value).css('display') != 'none'

      currentIndex = _.indexOf(backgrounds, current)
      nextIndex = (currentIndex + 1) % backgrounds.length
      $(backgrounds[currentIndex]).hide()
      $(backgrounds[nextIndex]).fadeIn()

      $($('.background-anchor')[currentIndex]).removeClass('active')
      $($('.background-anchor')[nextIndex]).addClass('active')

    switchBackgroundWrapper = ->
      switchBackground(4)
      setTimeout(switchBackgroundWrapper, 10 * 1000)

    setTimeout switchBackgroundWrapper, 10 * 1000

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
      .each (index)->
        if index == 0
          $(this).trigger('click')


