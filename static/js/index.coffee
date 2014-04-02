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
    .each (index)->
      if index == 0
        $(this).trigger('click')


