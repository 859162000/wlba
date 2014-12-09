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

    $('.mobile-app-top').bind('mouseenter',(e)->
      $('.mobile-app-top-prompt').show()
    )

    $('.mobile-app-top-prompt').bind('mouseleave',(e)->
      $(this).hide()
    )


    $('.mobile-app-bottom').bind('mouseenter',(e)->
      $('.mobile-app-bottom-prompt').show()
    )

    $('.mobile-app-bottom-prompt').bind('mouseleave',(e)->
      $(this).hide()
    )
