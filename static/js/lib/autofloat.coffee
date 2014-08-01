define ['jquery', 'underscore'], ($, _)->
  element = $('*[data-role=float]')
  parent = element.parent().parent()
  element.parent().css('position', 'relative')
  parentHeight = parent.height() - 15
  selfHeight = element.height()

  setTop = ()->
    if !element || selfHeight >= parentHeight
      return
      
    scrollTop = $(window.document).scrollTop()
    parentTop = parent.offset().top
    element.css('width', element.width())
    element.css('position', 'absolute')
    if scrollTop < parentTop
      element.css('top', 0)
    else if scrollTop - parentTop + selfHeight < parentHeight
      element.css('top', scrollTop - parentTop)
    else if scrollTop - parentTop + selfHeight > parentHeight
      element.css('top', parentHeight - selfHeight)

  $(window.document).scroll (e)->
    setTop()

