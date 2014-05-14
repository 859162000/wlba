require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ->
  $(document).ready ->
    $('[data-role=hover]').each (index, elem)->
      $(elem).mouseenter (e)->
        e.preventDefault()
        target = $(e.target).attr('data-target')
        $(target).show()

      $(elem).mouseleave (e)->
        e.preventDefault()
        target = $(e.target).attr('data-target')
        $(target).hide()
