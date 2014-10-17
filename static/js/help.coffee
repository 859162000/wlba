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

  $('.help-menu').on 'click', 'li', (e) ->
    e.preventDefault()
    #1.1 判断是否是active状态
    if($(this).hasClass('current'))
      return
    #1.2 清除原有的active状态
    $('.help-menu li.current').removeClass('current');
    $(this).addClass('current');

    #2.1 清除原有内容的active状态
    $('.help-box').removeClass('active')
    $('.list-item').removeClass('active')
    #2.2 重置现有内容的状态
    tar = $(this)
    source = $('.help-box[data-source="' + tar.attr('data-target') + '"]')
    source.addClass('active')
    $('.list-item:eq(0)', source).addClass('active')


  $(window).load (e)->
    tar = $('.help-menu li:eq(0)')
    tar.addClass('current')
    source = $('.help-box[data-source="' + tar.attr('data-target') + '"]')
    source.addClass('active')
    $('.list-item:eq(0)', source).addClass('active')