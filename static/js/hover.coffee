require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ->
  $(document).ready ->
    $('[data-role=hover]').bind('mouseenter',(e)->
      e.preventDefault()
      target = $(e.target).attr('data-target')
      $(target).show()
    ).bind('mouseleave', (e)->
      e.preventDefault()
      target = $(e.target).attr('data-target')
      $(target).hide()
    )
    $('[data-name=hoverbox]').bind('mouseenter',(e)->
      $(this).show()
    ).bind('mouseleave', (e)->
      $(this).hide()
    )
