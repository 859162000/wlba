require.config(
  paths:
    'jquery': 'lib/jquery.min'
)

require ['jquery'], ($) ->
  $('.list-container').on 'click', '.list-item-title', (e) ->
    item = $(this).parent()
    if(item.hasClass('active'))
      return

    $('.list-item').removeClass('active')
    item.addClass('active')
    return

  $('.host-items').on 'click', 'li', (e) ->
    #
    $('.help-box').removeClass('active')


  $(window).load (e)->
    tar = $('.help-menu li:eq(0)')
    tar.addClass('current')
    source = $('.help-box[data-source="' + tar.attr('data-target') + '"]')
    source.addClass('active')
    $('.list-item:eq(0)', source).addClass('active')