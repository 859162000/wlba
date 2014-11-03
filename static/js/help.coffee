require.config(
  paths:
    'jquery': 'lib/jquery.min'
)

require ['jquery'], ($) ->
  $('.list-container').on 'click', '.list-item-title', (e) ->
    item = $(this).parent()
    if(item.hasClass('active'))
      item.removeClass('active');
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
    #$('.list-item:eq(0)', source).addClass('active')

  $('.hot-items').on 'click', 'li', (e) ->
    e.preventDefault()
    topicId = $('a', $(this)).attr('data-topic')
    contentId = $('a', $(this)).attr('data-item')

    topic = $('.help-box[data-source="' + topicId + '"]')
    item = $('.list-item[data-source="' + contentId + '"]', topic)
    menu = $('.help-menu li[data-target="' + topicId + '"]')

    #1.2 清除原有的active状态
    $('.help-menu li.current').removeClass('current');
    menu.addClass('current');

    #2.1 清除原有内容的active状态
    $('.help-box').removeClass('active')
    $('.list-item').removeClass('active')
    #2.2 重置现有内容的状态
    topic.addClass('active')
    item.addClass('active')

  $(window).load (e)->
    tar = $('.help-menu li:eq(0)')
    tar.addClass('current')
    source = $('.help-box[data-source="' + tar.attr('data-target') + '"]')
    if !source.hasClass('active')
      source.addClass('active')
    #$('.list-item:eq(0)', source).addClass('active')