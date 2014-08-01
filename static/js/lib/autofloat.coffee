define ['jquery', 'underscore'], ($, _)->
  element = $('*[data-role=float]')
  parent = element.parent().parent()
  element.parent().css('position', 'relative')
  parentHeight = parent.height() - 15
  selfHeight = element.height()
  element.css('width', element.width())
  scrollTimeout = null

  setTop = ()->
    if !element || selfHeight >= parentHeight
      return

    scrollTop = $(window.document).scrollTop()
    parentTop = parent.offset().top

    element.css('position', 'absolute')
    if scrollTop < parentTop + 15
      element.animate({top: 0})
    else if scrollTop - parentTop + selfHeight <= parentHeight
      element.animate({top: scrollTop - parentTop - 15})
    else if scrollTop - parentTop + selfHeight > parentHeight
      element.animate({top: parentHeight - selfHeight})

  $(window.document).scroll (e)->
    if scrollTimeout
      clearTimeout(scrollTimeout)
      scrollTimeout = null
    scrollTimeout = setTimeout(setTop,100)

