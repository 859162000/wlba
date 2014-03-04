require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ($)->
  $(document).ready ->

    # setup the background switcher
    switchBackground = (max)->
      imageUrl = $('.big-background').css('background-image')
      matches = imageUrl.match(/\/bg(\d).jpg/)
      if matches.length == 2
        current = parseInt(matches[1]) + 1
        if current > max
          current = 1

        $('.big-background').css 'background-image',
          imageUrl.replace /\/bg\d.jpg/, '/bg' + current + '.jpg'

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


